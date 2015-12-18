# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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


class Entry(object):

    def __init__(self, number, row):
        self.number = number
        self.row = row
        self.user = None
        self.voicemail = None
        self.line = None
        self.sip = None
        self.sccp = None
        self.extension = None
        self.incall = None
        self.cti_profile = None

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
        }

    def create(self, resource, creator):
        fields = self.row[resource]
        setattr(self, resource, creator.create(fields))

    def associate(self, associator):
        associator.associate(self)

    def extract_field(self, resource, fieldname):
        return self.row.get(resource, {}).get(fieldname)

    def get_resource(self, resource):
        return getattr(self, resource, None)


class EntryCreator(object):

    def __init__(self, creators):
        self.creators = creators

    def create(self, line):
        row = line.parse()
        entry = Entry(line.position, row)
        entry.create('user', self.creators['user'])
        entry.create('voicemail', self.creators['voicemail'])
        entry.create('line', self.creators['line'])
        entry.create('extension', self.creators['extension'])
        entry.create('incall', self.creators['incall'])
        entry.create('cti_profile', self.creators['cti_profile'])
        self.create_endpoint(entry)
        return entry

    def create_endpoint(self, entry):
        endpoint = entry.extract_field('line', 'endpoint')
        if endpoint == 'sip':
            entry.create('sip', self.creators['sip'])
        elif endpoint == 'sccp':
            entry.create('sccp', self.creators['sccp'])


class EntryAssociator(object):

    def __init__(self, associators):
        self.associators = associators

    def associate(self, entry):
        for associator in self.associators.values():
            associator.associate(entry)
