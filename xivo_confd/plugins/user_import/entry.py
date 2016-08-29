# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.helpers import errors


class Entry(object):

    def __init__(self, number, entry_dict):
        self.number = number
        self.entry_dict = entry_dict
        self.user = None
        self.entity = None
        self.voicemail = None
        self.line = None
        self.sip = None
        self.sccp = None
        self.extension = None
        self.incall = None
        self.cti_profile = None
        self.call_permissions = []

    def extract_ids(self):
        return {
            'row_number': self.number,
            'user_id': self.user.id if self.user else None,
            'user_uuid': self.user.uuid if self.user else None,
            'voicemail_id': self.voicemail.id if self.voicemail else None,
            'line_id': self.line.id if self.line else None,
            'sip_id': self.sip.id if self.sip else None,
            'sccp_id': self.sccp.id if self.sccp else None,
            'extension_id': self.extension.id if self.extension else None,
            'incall_extension_id': self.incall.id if self.incall else None,
            'cti_profile_id': self.cti_profile.id if self.cti_profile else None,
            'call_permission_ids': self.extract_call_permission_ids(),
        }

    def extract_call_permission_ids(self):
        permissions = self.call_permissions or []
        return [permission.id for permission in permissions]

    def find(self, resource, creator):
        model = self.get_resource(resource)
        if model:
            return True

        fields = self.entry_dict[resource]
        model = creator.find(fields)
        if model:
            setattr(self, resource, model)
            return True
        return False

    def create(self, resource, creator):
        fields = self.entry_dict[resource]
        setattr(self, resource, creator.create(fields))

    def find_or_create(self, resource, creator):
        if not self.find(resource, creator):
            self.create(resource, creator)

    def update(self, resource, creator):
        model = self.get_resource(resource)
        if model:
            fields = self.entry_dict[resource]
            creator.update(fields, model)

    def extract_field(self, resource, fieldname):
        return self.entry_dict.get(resource, {}).get(fieldname)

    def get_resource(self, resource):
        return getattr(self, resource, None)


class EntryCreator(object):

    def __init__(self, creators):
        self.creators = creators

    def create(self, row):
        entry_dict = row.parse()
        entry = Entry(row.position, entry_dict)
        entry.create('user', self.creators['user'])
        entry.find('entity', self.creators['entity'])
        entry.find_or_create('voicemail', self.creators['voicemail'])
        entry.find_or_create('call_permissions', self.creators['call_permissions'])
        entry.find_or_create('line', self.creators['line'])
        entry.find_or_create('extension', self.creators['extension'])
        entry.find_or_create('incall', self.creators['incall'])
        entry.find_or_create('cti_profile', self.creators['cti_profile'])
        self.create_endpoint(entry)
        return entry

    def create_endpoint(self, entry):
        endpoint = entry.extract_field('line', 'endpoint')
        if endpoint == 'sip':
            entry.find_or_create('sip', self.creators['sip'])
        elif endpoint == 'sccp':
            entry.find_or_create('sccp', self.creators['sccp'])


class EntryAssociator(object):

    def __init__(self, associators):
        self.associators = associators

    def associate(self, entry):
        for associator in self.associators.values():
            associator.associate(entry)


class EntryFinder(object):

    def __init__(self, user_dao, entity_dao, voicemail_dao, user_voicemail_dao, cti_profile_dao,
                 user_cti_profile_dao, line_dao, user_line_dao, line_extension_dao,
                 sip_dao, sccp_dao, extension_dao, incall_dao, call_permission_dao,
                 user_call_permission_dao):
        self.user_dao = user_dao
        self.entity_dao = entity_dao
        self.voicemail_dao = voicemail_dao
        self.user_voicemail_dao = user_voicemail_dao
        self.cti_profile_dao = cti_profile_dao
        self.user_cti_profile_dao = user_cti_profile_dao
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

        entry.cti_profile = self.user_cti_profile_dao.find_profile_by_userid(user.id)

        entity_id = entry.extract_field('entity', 'id')
        if entity_id:
            entry.entity = self.entity_dao.get_by(id=entity_id)

        user_call_permissions = self.user_call_permission_dao.find_all_by(user_id=user.id)
        for user_call_permission in user_call_permissions:
            entry.call_permissions.append(self.call_permission_dao.get_by(id=user_call_permission.call_permission_id))

        user_voicemail = self.user_voicemail_dao.find_by_user_id(user.id)
        if user_voicemail:
            entry.voicemail = self.voicemail_dao.get(user_voicemail.voicemail_id)

        user_line = self.user_line_dao.find_by(user_id=user.id, main_line=True)
        if user_line:
            self.attach_line_resources(entry, user_line)

        return entry

    def attach_line_resources(self, entry, user_line):
        entry.line = self.line_dao.get(user_line.line_id)
        line_extension = self.line_extension_dao.find_by(line_id=user_line.line_id, main_extension=True)
        if line_extension:
            entry.extension = self.extension_dao.get(line_extension.extension_id)

        if entry.line.endpoint == "sip":
            entry.sip = self.sip_dao.get(entry.line.endpoint_id)
        elif entry.line.endpoint == "sccp":
            entry.sccp = self.sccp_dao.get(entry.line.endpoint_id)

        line_incalls = self.incall_dao.find_all_line_extensions_by_line_id(user_line.line_id)
        if len(line_incalls) > 1:
            raise errors.not_permitted('Cannot update when user has multiple incalls')
        elif len(line_incalls) == 1:
            entry.incall = self.extension_dao.get(line_incalls[0].extension_id)


class EntryUpdater(object):

    def __init__(self, creators, associators, finder):
        self.creators = creators
        self.associators = associators
        self.finder = finder

    def update_row(self, row):
        entry = self.finder.get_entry(row)
        self.create_missing_resources(entry)
        self.associate_resources(entry)
        self.update_resources(entry)
        return entry

    def create_missing_resources(self, entry):
        entry.find_or_create('voicemail', self.creators['voicemail'])
        entry.find_or_create('call_permissions', self.creators['call_permissions'])
        entry.find_or_create('extension', self.creators['extension'])
        entry.find_or_create('incall', self.creators['incall'])
        entry.find_or_create('cti_profile', self.creators['cti_profile'])
        entry.find_or_create('line', self.creators['line'])
        self.find_or_create_endpoint(entry)

    def find_or_create_endpoint(self, entry):
        endpoint = entry.extract_field('line', 'endpoint')
        if endpoint == 'sip':
            entry.find_or_create('sip', self.creators['sip'])
        elif endpoint == 'sccp':
            entry.find_or_create('sccp', self.creators['sccp'])

    def associate_resources(self, entry):
        for associator in self.associators.values():
            associator.update(entry)

    def update_resources(self, entry):
        for resource, creator in self.creators.iteritems():
            entry.update(resource, creator)
