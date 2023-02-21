# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from http import HTTPStatus

from requests import HTTPError
from xivo_dao.helpers.db_manager import Session
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.helpers.exception import NotFoundError, ResourceError, InputError
from xivo_dao.resources.switchboard import dao as switchboard_dao

from .schema import UserListItemSchema, UserSchema, UserListItemSchemaPut


class UserMiddleWare:
    def __init__(self, service, wazo_user_service, middleware_handle):
        self._service = service
        self._wazo_user_service = wazo_user_service
        self._middleware_handle = middleware_handle
        self._schema = UserListItemSchema()
        self._schema_update = UserSchema()
        self._schema_update_recursive = UserListItemSchemaPut()

    def create_associate_line(self, user_id, line_body, tenant_uuid, tenant_uuids):
        line = self._middleware_handle.get('line').create(
            line_body, tenant_uuid, tenant_uuids
        )
        self._middleware_handle.get('user_line_association').associate(
            user_id, line['id'], tenant_uuids
        )
        return line

    def associate_line_device(self, line, device_id, tenant_uuid, tenant_uuids):
        try:
            self._middleware_handle.get('device').assign_tenant(device_id, tenant_uuid)
        except Exception as e:
            if e is not NotFoundError:
                raise e
        self._middleware_handle.get('line_device_association').associate(
            line['id'], device_id, tenant_uuid, tenant_uuids
        )

    def create_line(self, user_id, line_body, tenant_uuid, tenant_uuids):
        line = self.create_associate_line(user_id, line_body, tenant_uuid, tenant_uuids)

        device_id = line_body.get('device_id', None)
        if device_id:
            self.associate_line_device(line, device_id, tenant_uuid, tenant_uuids)
            line['device_id'] = device_id
        return line

    def create(self, body, tenant_uuid, tenant_uuids):
        forwards = body.pop('forwards', None) or []
        fallbacks = body.pop('fallbacks', None) or []

        form = self._schema.load(body)
        form['tenant_uuid'] = tenant_uuid

        auth = form.pop('auth', None)
        lines = form.pop('lines', None) or []
        incalls = form.pop('incalls', None) or []
        groups = form.pop('groups', None) or []
        switchboards = form.pop('switchboards', None) or []
        voicemail = form.pop('voicemail', None)
        agent = form.pop('agent', {})

        model = User(**form)
        model = self._service.create(model)
        user_dict = self._schema.dump(model)
        user_dict['lines'] = []
        user_dict['incalls'] = []
        user_dict['groups'] = []
        user_dict['switchboards'] = []

        if voicemail:
            user_voicemail_middleware = self._middleware_handle.get('user_voicemail')
            voicemail_id = voicemail.get('id')
            if voicemail_id:
                voicemail_middleware = self._middleware_handle.get('voicemail')
                user_voicemail_middleware.associate(
                    model.uuid, voicemail_id, tenant_uuids
                )
                voicemail = voicemail_middleware.get(voicemail_id, tenant_uuids)
            else:
                if not voicemail.get('name', None):
                    if model.lastname:
                        voicemail['name'] = f"{model.firstname} {model.lastname}"
                    else:
                        voicemail['name'] = model.firstname
                voicemail = user_voicemail_middleware.create_voicemail(
                    model.uuid,
                    voicemail,
                    tenant_uuids,
                )
        user_dict['voicemail'] = voicemail

        if lines:
            for line_body in lines:
                line = self.create_line(
                    user_dict['id'], line_body, tenant_uuid, tenant_uuids
                )
                user_dict['lines'].append(line)

            Session.expire(model, ['user_lines'])

        def process_context(context_name, extension_number):
            existing_context = self._middleware_handle.get('context').get(
                tenant_uuids=tenant_uuids, name=context_name
            )
            if existing_context['type'] != 'incall':
                raise InputError(
                    "Context associated to the extension is not of type 'incall'"
                )
            # verify range, if no existing range-> create one
            range_found = False
            for r in existing_context['incall_ranges']:
                if r['start'] <= extension_number <= r['end']:
                    range_found = True
                    break
            if not range_found:
                existing_context['incall_ranges'].append(
                    {
                        'start': extension_number,
                        'end': extension_number,
                        'did_length': len(extension_number),
                    }
                )
                self._middleware_handle.get('context').update(
                    existing_context['id'], existing_context, tenant_uuids
                )

        def process_incall(extension_id, user_id, incall_id=None):
            if not incall_id:
                incall = self._middleware_handle.get('incall').create(
                    {'destination': {'type': 'user', 'user_id': user_id}}, tenant_uuid
                )
            else:
                incall = self._middleware_handle.get('incall').get(
                    incall_id, tenant_uuids
                )

                if incall['destination']['type'] == 'none':
                    incall['destination'] = {'type': 'user', 'user_id': user_id}
                    self._middleware_handle.get('incall').update(
                        incall_id, incall, tenant_uuids
                    )

                elif (
                    incall['destination']['type'] != 'user'
                    or incall['destination']['user_id'] != user_id
                ):
                    raise InputError(
                        "Existing incall does not have the new user as a destination"
                    )

            self._middleware_handle.get('incall_extension_association').associate(
                incall['id'], extension_id, tenant_uuids
            )

            return incall

        for incall_body in incalls:
            for extension_body in incall_body['extensions']:
                extension_id = extension_body.get('id', None)
                if extension_id:
                    extension = self._middleware_handle.get('extension').get(
                        extension_id, tenant_uuids
                    )
                    if not extension:
                        raise InputError("Extension not found")

                else:
                    try:
                        extension = self._middleware_handle.get('extension').create(
                            extension_body, tenant_uuids
                        )
                    except ResourceError as e:
                        if str(e).startswith(
                            'Resource Error - Extension already exists'
                        ):
                            extension = self._middleware_handle.get('extension').get_by(
                                exten=extension_body['exten'],
                                context=extension_body['context'],
                                tenant_uuids=tenant_uuids,
                            )
                        else:
                            raise e

                process_context(extension['context'], extension['exten'])

                incall = process_incall(
                    extension['id'],
                    user_dict['id'],
                    (
                        {} if not extension.get('incall', None) else extension['incall']
                    ).get('id', None),
                )

                extension_body['id'] = extension['id']

            incall_body['id'] = incall['id']
            user_dict['incalls'].append(incall_body)

        if groups:
            self._middleware_handle.get('user_group_association').associate_all_groups(
                {'groups': groups}, user_dict['uuid']
            )
        user_dict['groups'] = groups

        for _switchboard in switchboards:
            # retrieve the switchboard to add the new user to its members
            switchboard = switchboard_dao.get(
                _switchboard['uuid'], tenant_uuids=tenant_uuids
            )
            members = []
            for user_member in switchboard.user_members:
                members.append({'uuid': user_member.uuid})
            members.append({'uuid': user_dict['uuid']})
            self._middleware_handle.get('switchboard_member').associate(
                {'users': members}, _switchboard['uuid'], tenant_uuids
            )
        user_dict['switchboards'] = switchboards

        if agent:
            queues = agent['queues']
            created_agent = self._middleware_handle.get('agent').create(
                agent, tenant_uuid, tenant_uuids
            )
            created_agent['queues'] = queues
            self._middleware_handle.get('user_agent_association').associate(
                user_dict['uuid'], created_agent['id'], tenant_uuids
            )
            user_dict['agent'] = created_agent

        if forwards:
            self._middleware_handle.get('user_forward_association').associate(
                user_dict['uuid'], forwards
            )
            user_dict['forwards'] = self._middleware_handle.get(
                'user_forward_association'
            ).get(user_dict['uuid'])

        if fallbacks:
            self._middleware_handle.get('user_fallback_association').associate(
                user_dict['uuid'], fallbacks
            )
            user_dict['fallbacks'] = self._middleware_handle.get(
                'user_fallback_association'
            ).get(user_dict['uuid'])

        if auth:
            auth['uuid'] = user_dict['uuid']
            auth['tenant_uuid'] = user_dict['tenant_uuid']
            user_dict['auth'] = self._wazo_user_service.create(auth)

        return user_dict

    def delete_line(self, device_id, line_id, user_id, tenant_uuid, tenant_uuids):
        if device_id:
            self._middleware_handle.get('device').reset_autoprov(device_id, tenant_uuid)

        # process the line itself
        self._middleware_handle.get('user_line_association').dissociate(
            user_id, line_id, tenant_uuids
        )
        self._middleware_handle.get('line').delete(
            line_id, tenant_uuid, tenant_uuids, recursive=True
        )

    def delete(self, user_id, tenant_uuid, tenant_uuids, recursive=False):
        user = self._service.get(user_id, tenant_uuids=tenant_uuids)
        if not recursive:
            self._service.delete(user)
        else:
            if user.agent:
                agentid = user.agentid
                self._middleware_handle.get('user_agent_association').dissociate(
                    user.uuid, tenant_uuids
                )
                self._middleware_handle.get('agent').delete(agentid, tenant_uuids)

            if user.groups:
                # dissociation
                self._middleware_handle.get(
                    'user_group_association'
                ).associate_all_groups({'groups': []}, user.uuid)

            if user.voicemail:
                self._middleware_handle.get('user_voicemail').delete_voicemail(
                    user.uuid, tenant_uuids
                )

            for line in user.lines:
                # process the device associated to the line
                self.delete_line(
                    line.device, line.id, user.uuid, tenant_uuid, tenant_uuids
                )

                Session.expire(user, ['user_lines'])

            for incall in user.incalls:
                for extension in incall.extensions:
                    self._middleware_handle.get(
                        'incall_extension_association'
                    ).dissociate(incall.id, extension.id, tenant_uuids)
                    self._middleware_handle.get('extension').delete(
                        extension.id, tenant_uuids
                    )
                self._middleware_handle.get('incall').delete(incall.id, tenant_uuids)

            for switchboard in user.switchboards:
                members = []
                for user_member in switchboard.user_members:
                    if user_member.uuid != user.uuid:
                        members.append({'uuid': user_member.uuid})
                self._middleware_handle.get('switchboard_member').associate(
                    {'users': members}, switchboard.uuid, tenant_uuids
                )
            Session.expire(user, ['switchboard_member_users'])

            self._service.delete(user)

            try:
                self._wazo_user_service.delete(user.uuid)
            except HTTPError as e:
                if e.response.status_code != HTTPStatus.NOT_FOUND:
                    raise e

    def parse_and_update(self, model, body, **kwargs):
        form = self._schema_update.load(body, partial=True)
        updated_fields = self.find_updated_fields(model, form)
        for name, value in form.items():
            setattr(model, name, value)
        self._service.edit(model, updated_fields=updated_fields, **kwargs)

    def find_updated_fields(self, model, form):
        updated_fields = []
        for name, value in form.items():
            try:
                if getattr(model, name) != value:
                    updated_fields.append(name)
            except AttributeError:
                pass
        return updated_fields

    def update(self, user_id, body, tenant_uuid, tenant_uuids, recursive=False):
        user = self._service.get(user_id, tenant_uuids=tenant_uuids)
        if not recursive:
            self.parse_and_update(user, body)
        else:
            fallbacks = body.pop('fallbacks', None) or []
            forwards = body.pop('forwards', None) or []

            form = self._schema_update_recursive.load(body)

            groups = form.pop('groups', None) or []
            lines = form.pop('lines', None) or []

            if fallbacks:
                self._middleware_handle.get('user_fallback_association').associate(
                    user_id, fallbacks
                )

            if forwards:
                self._middleware_handle.get('user_forward_association').dissociate(
                    user_id
                )
                self._middleware_handle.get('user_forward_association').associate(
                    user_id, forwards
                )

            # groups
            self._middleware_handle.get('user_group_association').associate_all_groups(
                {'groups': groups}, user_id
            )

            # lines
            user = self._service.get(user_id, tenant_uuids=tenant_uuids)
            existing_lines = {el.id: el for el in user.lines}

            for line_body in lines:
                device_id = line_body.get('device_id', None)
                if 'id' in line_body and line_body['id'] in existing_lines:
                    old_device_id = existing_lines[line_body['id']].device_id
                    self._middleware_handle.get('line').update(
                        line_body['id'], line_body, tenant_uuid, tenant_uuids
                    )
                    # if device_id not the same, so we must dissociate the old one and associate the new line
                    if device_id != old_device_id:
                        self._middleware_handle.get('device').reset_autoprov(
                            old_device_id, tenant_uuid
                        )
                    self.associate_line_device(
                        {'id': line_body['id']}, device_id, tenant_uuid, tenant_uuids
                    )

                    del existing_lines[line_body['id']]
                else:
                    line = self.create_associate_line(
                        user_id, line_body, tenant_uuid, tenant_uuids
                    )
                    if device_id:
                        self.associate_line_device(
                            line, device_id, tenant_uuid, tenant_uuids
                        )
            for line_id in existing_lines:
                self.delete_line(
                    existing_lines[line_id].device,
                    line_id,
                    user.uuid,
                    tenant_uuid,
                    tenant_uuids,
                )
