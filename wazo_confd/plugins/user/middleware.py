# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from http import HTTPStatus

from requests import HTTPError
from xivo_dao.helpers.db_manager import Session
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.helpers.exception import NotFoundError, ResourceError, InputError
from xivo_dao.resources.switchboard import dao as switchboard_dao

from .schema import UserListItemSchema, UserSchema, UserListItemSchemaPut
from ...middleware import ResourceMiddleware


class UserMiddleWare(ResourceMiddleware):
    def __init__(self, service, wazo_user_service, middleware_handle):
        super().__init__(service, UserListItemSchema(), update_schema=UserSchema())
        self._wazo_user_service = wazo_user_service
        self._middleware_handle = middleware_handle
        self._update_schema_recursive = UserListItemSchemaPut()

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
            # if not found => the device is not on the master tenant
            if e is not NotFoundError:
                try:
                    # check if the device is on the current tenant
                    self._middleware_handle.get('device').get(
                        device_id, tenant_uuid=tenant_uuid
                    )
                except Exception as e:
                    # if the device is not on the current tenant
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

    def create_voicemail(self, user_model, voicemail, tenant_uuids):
        user_voicemail_middleware = self._middleware_handle.get('user_voicemail')
        voicemail_id = voicemail.get('id')
        if voicemail_id:
            voicemail_middleware = self._middleware_handle.get('voicemail')
            user_voicemail_middleware.associate(
                user_model.uuid, voicemail_id, tenant_uuids
            )
            voicemail = voicemail_middleware.get(voicemail_id, tenant_uuids)
        else:
            if not voicemail.get('name', None):
                if user_model.lastname:
                    voicemail['name'] = f"{user_model.firstname} {user_model.lastname}"
                else:
                    voicemail['name'] = user_model.firstname
            voicemail = user_voicemail_middleware.create_voicemail(
                user_model.uuid,
                voicemail,
                tenant_uuids,
            )
        return voicemail

    def create_or_get(self, extension_body, tenant_uuids):
        try:
            extension = self._middleware_handle.get('extension').create(
                extension_body, tenant_uuids
            )
        except ResourceError as e:
            if str(e).startswith('Resource Error - Extension already exists'):
                extension = self._middleware_handle.get('extension').get_by(
                    exten=extension_body['exten'],
                    context=extension_body['context'],
                    tenant_uuids=tenant_uuids,
                )
            else:
                raise e
        return extension

    def update_incall(self, user_id, incall, tenant_uuids):
        if 'destination' not in incall or incall['destination']['type'] == 'none':
            incall['destination'] = {'type': 'user', 'user_id': user_id}
            self._middleware_handle.get('incall').update(
                incall['id'], incall, tenant_uuids
            )

        elif (
            incall['destination']['type'] != 'user'
            or incall['destination']['user_id'] != user_id
        ):
            raise InputError(
                "Existing incall does not have the new user as a destination"
            )

    def update_context(self, context_name, extension_number, tenant_uuids):
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
            voicemail = self.create_voicemail(model, voicemail, tenant_uuids)
        user_dict['voicemail'] = voicemail

        if lines:
            for line_body in lines:
                line = self.create_line(
                    user_dict['id'], line_body, tenant_uuid, tenant_uuids
                )
                user_dict['lines'].append(line)

            Session.expire(model, ['user_lines'])

        def process_incall(extension_id, user_id, incall_id=None):
            if not incall_id:
                incall = self._middleware_handle.get('incall').create(
                    {'destination': {'type': 'user', 'user_id': user_id}}, tenant_uuid
                )
            else:
                incall = self._middleware_handle.get('incall').get(
                    incall_id, tenant_uuids
                )
                self.update_incall(user_id, incall, tenant_uuids)

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
                    extension = self.create_or_get(extension_body, tenant_uuids)

                self.update_context(
                    extension['context'], extension['exten'], tenant_uuids
                )

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
            queues = None
            try:
                queues = agent['queues']
            except KeyError:
                pass
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
                    try:
                        self._middleware_handle.get('extension').delete(
                            extension.id, tenant_uuids
                        )
                    except ResourceError as e:
                        if not str(e).startswith(
                            'Resource Error - Extension is associated'
                        ):
                            raise e
                # set incall destination to none
                self._middleware_handle.get('incall').update(
                    incall.id, {'destination': {'type': 'none'}}, tenant_uuids
                )

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

    def update_incalls(self, user, incalls, tenant_uuid, tenant_uuids):
        def create_or_update_incall(incall_id, incall_body, user_id, tenant_uuid):
            if incall_id:
                # update incall
                self.update_incall(user_id, incall_body, tenant_uuids)
                return None
            else:
                # new_incall=create incall
                new_incall = self._middleware_handle.get('incall').create(
                    {
                        **incall_body,
                        'destination': {'type': 'user', 'user_id': user_id},
                    },
                    tenant_uuid,
                )
                return new_incall

        def create_or_update_extension(extension_id, extension_body, tenant_uuids):
            if extension_id:
                # update extension
                self._middleware_handle.get('extension').update(
                    extension_id, extension_body, tenant_uuids
                )
                return None
            else:
                # new_extension=create extension
                new_extension = self.create_or_get(extension_body, tenant_uuids)
                return new_extension

        existing_incalls_ids = {}
        existing_extensions_ids = {}
        # dissociate all existing incalls / extensions
        for i in user.incalls:
            existing_incalls_ids[i.id] = None
            for e in i.extensions:
                existing_extensions_ids[e.id] = None
                self._middleware_handle.get('incall_extension_association').dissociate(
                    i.id, e.id, tenant_uuids
                )

        for incall_body in incalls:
            incall_id = incall_body.get('id', None)
            new_incall = create_or_update_incall(
                incall_id, incall_body, user.id, tenant_uuid
            )

            for extension_body in incall_body['extensions']:
                extension_id = extension_body.get('id', None)
                new_extension = create_or_update_extension(
                    extension_id, extension_body, tenant_uuids
                )

                if new_extension:
                    if new_incall:
                        # associate new incall and new extension
                        self._middleware_handle.get(
                            'incall_extension_association'
                        ).associate(new_incall['id'], new_extension['id'], tenant_uuids)
                    else:
                        # as there is a new extension, context should be updated
                        self.update_context(
                            new_extension['context'],
                            new_extension['exten'],
                            tenant_uuids,
                        )
                        # associate old incall and new extension
                        self._middleware_handle.get(
                            'incall_extension_association'
                        ).associate(incall_id, new_extension['id'], tenant_uuids)
                else:
                    if new_incall:
                        # associate new incall and old extension
                        self._middleware_handle.get(
                            'incall_extension_association'
                        ).associate(new_incall['id'], extension_id, tenant_uuids)

                # the extension has been processed, so removed from the list
                if extension_id in existing_extensions_ids:
                    del existing_extensions_ids[extension_id]

            # the incall has been processed, so removed from the list
            if incall_id in existing_incalls_ids:
                del existing_incalls_ids[incall_id]

        # all the incalls (that have not been processed previously)
        # are not used anymore so can be removed
        for i in existing_incalls_ids:
            self._middleware_handle.get('incall').delete(i, tenant_uuids)

        # all the extensions (that have not been processed previously)
        # are not used anymore so can be removed
        for e in existing_extensions_ids:
            try:
                self._middleware_handle.get('extension').delete(e, tenant_uuids)
            except ResourceError as e:
                if not str(e).startswith('Resource Error - Extension is associated'):
                    raise e

    def update(self, user_id, body, tenant_uuid, tenant_uuids, recursive=False):
        user = self._service.get(user_id, tenant_uuids=tenant_uuids)
        if not recursive:
            self.parse_and_update(user, body)
        else:
            fallbacks = body.pop('fallbacks', None) or []
            forwards = body.pop('forwards', None) or []
            switchboards = body.pop('switchboards', None) or []

            form = self._update_schema_recursive.load(body)

            groups = form.pop('groups', None) or []
            lines = form.pop('lines', None) or []
            agent = form.pop('agent', None) or []
            voicemail = form.pop('voicemail', None)
            incalls = form.pop('incalls', None) or []

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
                        line_body['id'],
                        line_body,
                        tenant_uuid,
                        tenant_uuids,
                        recursive=True,
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

            if agent:
                existing_agent_id = user.agentid
                provided_agent_id = agent.get('id', None)

                # if the agent ids are the same -> update
                if existing_agent_id and existing_agent_id == provided_agent_id:
                    self._middleware_handle.get('agent').update(
                        existing_agent_id, agent, tenant_uuids
                    )
                else:
                    # if no existing agent and no provided agent id -> create/associate
                    if not existing_agent_id and not provided_agent_id:
                        agent = self._middleware_handle.get('agent').create(
                            agent, tenant_uuid, tenant_uuids
                        )
                        self._middleware_handle.get('user_agent_association').associate(
                            user_id, agent['id'], tenant_uuids
                        )
                    else:
                        # if no existing agent and there is a provided agent id -> associate
                        if not existing_agent_id and provided_agent_id:
                            # even if details are provided for the agent (firstname,
                            # language, ...), there are ignored
                            # there is only an association, no update here
                            self._middleware_handle.get(
                                'user_agent_association'
                            ).associate(user_id, provided_agent_id, tenant_uuids)
                        else:
                            # if there is an existing agent id and no provided agent id
                            # -> dissociate/delete + create/associate
                            if not provided_agent_id and existing_agent_id:
                                self._middleware_handle.get(
                                    'user_agent_association'
                                ).dissociate(user_id, tenant_uuids)
                                self._middleware_handle.get('agent').delete(
                                    existing_agent_id, tenant_uuids
                                )

                                agent = self._middleware_handle.get('agent').create(
                                    agent, tenant_uuid, tenant_uuids
                                )
                                self._middleware_handle.get(
                                    'user_agent_association'
                                ).associate(user_id, agent['id'], tenant_uuids)

            for _switchboard in user.switchboards:
                self._middleware_handle.get('switchboard_member').dissociate(
                    str(user_id), _switchboard.uuid, tenant_uuids
                )

            self._middleware_handle.get(
                'switchboard_member'
            ).associate_user_to_switchboards(str(user_id), switchboards, tenant_uuids)

            if voicemail:
                if 'id' in voicemail and voicemail['id'] == user.voicemailid:
                    # update voicemail
                    self._middleware_handle.get('voicemail').update(
                        voicemail['id'], voicemail, tenant_uuids
                    )
                else:
                    # if existing voicemail attached
                    if user.voicemailid:
                        # detach voicemail and delete if not used by any other user
                        self._middleware_handle.get('user_voicemail').delete_voicemail(
                            user_id, tenant_uuids
                        )

                    self.create_voicemail(user, voicemail, tenant_uuids)

            self.update_incalls(user, incalls, tenant_uuid, tenant_uuids)
