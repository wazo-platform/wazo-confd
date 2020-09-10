# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from .constants import VALID_ENDPOINT_TYPES


class Entry:
    def __init__(self, number, entry_dict):
        self.number = number
        self.entry_dict = entry_dict
        self.context = None
        self.user = None
        self.wazo_user = None  # will be a dictionnary instead of sql object
        self.voicemail = None
        self.line = None
        self.sip = None
        self.sccp = None
        self.webrtc = None
        self.extension = None
        self.extension_incall = None
        self.incall = None
        self.call_permissions = []

    def extract_ids(self):
        if self.sip:
            sip_uuid = str(self.sip.uuid)
        elif self.webrtc:
            sip_uuid = str(self.webrtc.uuid)
        else:
            sip_uuid = None

        return {
            'row_number': self.number,
            'user_id': self.user.id if self.user else None,
            'user_uuid': self.user.uuid if self.user else None,
            'voicemail_id': self.voicemail.id if self.voicemail else None,
            'line_id': self.line.id if self.line else None,
            'sip_uuid': sip_uuid,
            'sccp_id': self.sccp.id if self.sccp else None,
            'extension_id': self.extension.id if self.extension else None,
            'incall_extension_id': self.extension_incall.id
            if self.extension_incall
            else None,
            'call_permission_ids': self.extract_call_permission_ids(),
        }

    def extract_call_permission_ids(self):
        permissions = self.call_permissions or []
        return [permission.id for permission in permissions]

    def find(self, resource, creator, tenant_uuid):
        model = self.get_resource(resource)
        if model:
            return True

        fields = self.entry_dict[resource]
        model = creator.find(fields, tenant_uuid)
        if model:
            setattr(self, resource, model)
            return True
        return False

    def create(self, resource, creator, tenant_uuid):
        fields = self.entry_dict[resource]
        setattr(self, resource, creator.create(fields, tenant_uuid))

    def find_or_create(self, resource, creator, tenant_uuid):
        if not self.find(resource, creator, tenant_uuid):
            self.create(resource, creator, tenant_uuid)

    def update(self, resource, creator):
        model = self.get_resource(resource)
        if model:
            fields = self.entry_dict[resource]
            creator.update(fields, model)

    def extract_field(self, resource, fieldname):
        return self.entry_dict.get(resource, {}).get(fieldname)

    def get_resource(self, resource):
        return getattr(self, resource, None)


class EntryCreator:
    def __init__(self, creators):
        self.creators = creators

    def create(self, row, tenant_uuid):
        entry_dict = row.parse()
        entry = Entry(row.position, entry_dict)
        entry.find('context', self.creators['context'], tenant_uuid)
        entry.create('user', self.creators['user'], tenant_uuid)
        entry.create('wazo_user', self.creators['wazo_user'], tenant_uuid)
        entry.find_or_create('voicemail', self.creators['voicemail'], tenant_uuid)
        entry.find_or_create(
            'call_permissions', self.creators['call_permissions'], tenant_uuid
        )
        entry.find_or_create('line', self.creators['line'], tenant_uuid)
        entry.find_or_create('extension', self.creators['extension'], tenant_uuid)
        entry.find_or_create(
            'extension_incall', self.creators['extension_incall'], tenant_uuid
        )
        entry.find_or_create('incall', self.creators['incall'], tenant_uuid)
        self.create_endpoint(entry, tenant_uuid)
        return entry

    def create_endpoint(self, entry, tenant_uuid):
        endpoint = entry.extract_field('line', 'endpoint')
        if endpoint not in VALID_ENDPOINT_TYPES:
            return
        entry.find_or_create(endpoint, self.creators[endpoint], tenant_uuid)


class EntryAssociator:
    def __init__(self, associators):
        self.associators = associators

    def associate(self, entry):
        for associator in self.associators.values():
            associator.associate(entry)


class EntryFinder:
    def __init__(
        self,
        user_dao,
        voicemail_dao,
        user_voicemail_dao,
        line_dao,
        user_line_dao,
        line_extension_dao,
        sip_dao,
        sccp_dao,
        extension_dao,
        incall_dao,
        call_permission_dao,
        user_call_permission_dao,
    ):
        self.user_dao = user_dao
        self.voicemail_dao = voicemail_dao
        self.user_voicemail_dao = user_voicemail_dao
        self.line_dao = line_dao
        self.user_line_dao = user_line_dao
        self.line_extension_dao = line_extension_dao
        self.sip_dao = sip_dao
        self.sccp_dao = sccp_dao
        self.extension_dao = extension_dao
        self.incall_dao = incall_dao
        self.call_permission_dao = call_permission_dao
        self.user_call_permission_dao = user_call_permission_dao

    def get_entry(self, row):
        entry_dict = row.parse()
        entry = Entry(row.position, entry_dict)
        uuid = entry.extract_field('user', 'uuid')
        user = entry.user = self.user_dao.get_by(uuid=uuid)

        # Avoid to GET /users/uuid on wazo-auth
        email = {'address': user.email, 'confirmed': True} if user.email else None
        entry.wazo_user = {
            'uuid': user.uuid,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'username': user.username,
            'emails': [email] if email else [],
        }

        user_call_permissions = self.user_call_permission_dao.find_all_by(
            user_id=user.id
        )
        for user_call_permission in user_call_permissions:
            entry.call_permissions.append(
                self.call_permission_dao.get_by(
                    id=user_call_permission.call_permission_id
                )
            )

        user_voicemail = self.user_voicemail_dao.find_by_user_id(user.id)
        if user_voicemail:
            entry.voicemail = self.voicemail_dao.get(user_voicemail.voicemail_id)

        user_line = self.user_line_dao.find_by(user_id=user.id, main_line=True)
        if user_line:
            self.attach_line_resources(entry, user_line)

        incalls = self.incall_dao.find_all_by(user_id=user.id)
        if len(incalls) > 1:
            raise errors.not_permitted('Cannot update when user has multiple incalls')
        elif len(incalls) == 1:
            entry.extension_incall = self.extension_dao.get_by(
                type='incall', typeval=str(incalls[0].id)
            )
            entry.incall = incalls[0]

        return entry

    def attach_line_resources(self, entry, user_line):
        entry.line = self.line_dao.get(user_line.line_id)
        line_extension = self.line_extension_dao.find_by(
            line_id=user_line.line_id, main_extension=True
        )
        if line_extension:
            entry.extension = self.extension_dao.get(line_extension.extension_id)

        if entry.line.endpoint_sip_uuid:
            entry.sip = self.sip_dao.get(entry.line.endpoint_sip_uuid)
        elif entry.line.endpoint_sccp_id:
            entry.sccp = self.sccp_dao.get(entry.line.endpoint_sccp_id)


class EntryUpdater:
    def __init__(self, creators, associators, finder):
        self.creators = creators
        self.associators = associators
        self.finder = finder

    def update_row(self, row, tenant_uuid):
        entry = self.finder.get_entry(row)
        self.create_missing_resources(entry, tenant_uuid)
        self.associate_resources(entry)
        self.update_resources(entry)
        return entry

    def create_missing_resources(self, entry, tenant_uuid):
        entry.find_or_create('voicemail', self.creators['voicemail'], tenant_uuid)
        entry.find_or_create(
            'call_permissions', self.creators['call_permissions'], tenant_uuid
        )
        entry.find_or_create('extension', self.creators['extension'], tenant_uuid)
        entry.find_or_create(
            'extension_incall', self.creators['extension_incall'], tenant_uuid
        )
        entry.find_or_create('incall', self.creators['incall'], tenant_uuid)
        entry.find_or_create('line', self.creators['line'], tenant_uuid)
        self.find_or_create_endpoint(entry, tenant_uuid)

    def find_or_create_endpoint(self, entry, tenant_uuid):
        endpoint = entry.extract_field('line', 'endpoint')
        if endpoint not in VALID_ENDPOINT_TYPES:
            return
        entry.find_or_create(endpoint, self.creators[endpoint], tenant_uuid)

    def associate_resources(self, entry):
        for associator in self.associators.values():
            associator.update(entry)

    def update_resources(self, entry):
        for resource, creator in self.creators.items():
            entry.update(resource, creator)
