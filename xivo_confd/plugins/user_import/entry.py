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

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.usersip import UserSIP as SIPEndpoint
from xivo_dao.alchemy.sccpline import SCCPLine as SCCPEndpoint
from xivo_dao.resources.extension.model import Extension
from xivo_dao.resources.voicemail.model import Voicemail
from xivo_dao.resources.incall.model import Incall
from xivo_dao.resources.user_cti_profile.model import UserCtiProfile


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
        self.incall_extension = None
        self.incall_ring_seconds = None
        self.user_cti_profile = None

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
            'incall_extension_id': self.incall_extension.id if self.incall_extension else None,
            'cti_profile_id': self.user_cti_profile.cti_profile_id if self.user_cti_profile else None,
        }

    def create(self, resource, model_class, service):
        fields = self.row[resource]
        setattr(self, resource, service.create(model_class(**fields)))

    def create_user(self, service):
        if self.row['user']:
            self.create('user', User, service)

    def create_voicemail(self, service):
        if self.row['voicemail']:
            self.create('voicemail', Voicemail, service)

    def create_line(self, service):
        if self.row['line']:
            self.create('line', Line, service)

    def create_sip(self, service):
        if self.row['endpoint'] == 'sip':
            self.create('sip', SIPEndpoint, service)

    def create_sccp(self, service):
        if self.row['endpoint'] == 'sccp':
            self.create('sccp', SCCPEndpoint, service)

    def create_extension(self, service):
        extension = self.row['extension']
        if 'exten' in extension and 'context' in extension:
            self.create('extension', Extension, service)

    def create_incall_extension(self, service):
        fields = self.row['incall']
        if fields:
            extension = Extension(exten=self.row['incall']['exten'],
                                  context=self.row['incall']['context'])
            self.incall_extension = service.create(extension)

    def create_cti_profile(self, cti_profile_dao):
        fields = self.row['cti_profile']
        if fields:
            cti_profile_id = cti_profile_dao.get_id_by_name(fields['name'])
            self.user_cti_profile = UserCtiProfile(user_id=self.user.id,
                                                   cti_profile_id=cti_profile_id,
                                                   enabled=fields.get('enabled'))

    def associate(self, left, right, associator):
        left_resource = getattr(self, left)
        right_resource = getattr(self, right)
        if left_resource and right_resource:
            associator(left_resource, right_resource)

    def associate_incall(self, incall_dao):
        if self.user and self.incall_extension:
            incall = Incall.user_destination(self.user.id,
                                             self.incall_extension.id,
                                             ring_seconds=self.row['incall'].get('ring_seconds'))
            incall_dao.create(incall)

    def associate_cti_profile(self, service):
        if self.user and self.user_cti_profile:
            service.edit(self.user_cti_profile)


class EntryCreator(object):

    def __init__(self, user_service, voicemail_service, line_service, sip_service,
                 sccp_service, extension_service, cti_profile_dao,
                 user_cti_profile_service):
        self.user_service = user_service
        self.voicemail_service = voicemail_service
        self.line_service = line_service
        self.sip_service = sip_service
        self.sccp_service = sccp_service
        self.extension_service = extension_service
        self.cti_profile_dao = cti_profile_dao
        self.user_cti_profile_service = user_cti_profile_service

    def create(self, line):
        row = line.parse()
        entry = Entry(line.position, row)
        entry.create_user(self.user_service)
        entry.create_voicemail(self.voicemail_service)
        entry.create_line(self.line_service)
        entry.create_sip(self.sip_service)
        entry.create_sccp(self.sccp_service)
        entry.create_extension(self.extension_service)
        entry.create_incall_extension(self.extension_service)
        entry.create_cti_profile(self.cti_profile_dao)
        return entry


class EntryAssociator(object):

    def __init__(self, user_voicemail_service, user_line_service,
                 line_sip_service, line_sccp_service, line_extension_service,
                 incall_dao, user_cti_profile_service):
        self.user_voicemail_service = user_voicemail_service
        self.user_line_service = user_line_service
        self.line_sip_service = line_sip_service
        self.line_sccp_service = line_sccp_service
        self.line_extension_service = line_extension_service
        self.incall_dao = incall_dao
        self.user_cti_profile_service = user_cti_profile_service

    def associate(self, entry):
        entry.associate('user', 'voicemail', self.user_voicemail_service.associate_models)
        entry.associate('line', 'sip', self.line_sip_service.associate)
        entry.associate('line', 'sccp', self.line_sccp_service.associate)
        entry.associate('line', 'extension', self.line_extension_service.associate)
        entry.associate('user', 'line', self.user_line_service.associate)
        entry.associate_incall(self.incall_dao)
        entry.associate_cti_profile(self.user_cti_profile_service)
