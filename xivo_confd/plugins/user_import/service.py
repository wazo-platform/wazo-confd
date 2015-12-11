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

from xivo_dao.helpers import errors as error_msg

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.usersip import UserSIP as SIPEndpoint
from xivo_dao.alchemy.sccpline import SCCPLine as SCCPEndpoint
from xivo_dao.resources.extension.model import Extension
from xivo_dao.resources.voicemail.model import Voicemail
from xivo_dao.resources.incall.model import Incall
from xivo_dao.resources.user_cti_profile.model import UserCtiProfile

from xivo_dao.helpers.exception import ServiceError


class Entry(object):

    def __init__(self, row_number, user=None, voicemail=None, line=None, sip=None,
                 sccp=None, extension=None, incall_extension=None, user_cti_profile=None):
        self.row_number = row_number
        self.user = user
        self.voicemail = voicemail
        self.line = line
        self.sip = sip
        self.sccp = sccp
        self.extension = extension
        self.incall_extension = incall_extension
        self.incall_ring_seconds = None
        self.user_cti_profile = user_cti_profile

    @property
    def user_id(self):
        return self.user.id

    @property
    def voicemail_id(self):
        return self.voicemail.id if self.voicemail else None

    @property
    def line_id(self):
        return self.line.id if self.line else None

    @property
    def sip_id(self):
        return self.sip.id if self.sip else None

    @property
    def sccp_id(self):
        return self.sccp.id if self.sccp else None

    @property
    def extension_id(self):
        return self.extension.id if self.extension else None

    @property
    def incall_extension_id(self):
        return self.incall_extension.id if self.incall_extension else None

    @property
    def cti_profile_id(self):
        return self.user_cti_profile.cti_profile_id if self.user_cti_profile else None


class ImportService(object):

    def __init__(self, user_service, voicemail_service, user_voicemail_service,
                 line_service, sip_service, sccp_service, line_sip_service,
                 line_sccp_service, extension_service, line_extension_service,
                 user_line_service, incall_dao, cti_profile_dao, user_cti_profile_service):
        self.user_service = user_service
        self.voicemail_service = voicemail_service
        self.user_voicemail_service = user_voicemail_service
        self.line_service = line_service
        self.sip_service = sip_service
        self.sccp_service = sccp_service
        self.line_sip_service = line_sip_service
        self.line_sccp_service = line_sccp_service
        self.extension_service = extension_service
        self.line_extension_service = line_extension_service
        self.user_line_service = user_line_service
        self.incall_dao = incall_dao
        self.cti_profile_dao = cti_profile_dao
        self.user_cti_profile_service = user_cti_profile_service

    def import_rows(self, parser):
        created = []
        errors = []

        for line in parser:
            try:
                entry = self.import_row(line)
                created.append(entry)
            except ServiceError as e:
                errors.append(line.format_error(e))

        return created, errors

    def import_row(self, line):
        entry = self.create_entry(line)
        self.create_associations(entry)
        return entry

    def create_entry(self, line):
        row = line.parse()
        entry = Entry(line.position)
        entry.user = self.create_user(row['user'])
        entry.voicemail = self.create_voicemail(row['voicemail'])
        entry.line = self.create_line(row['line'])
        entry.extension = self.create_extension(row['extension'])
        entry.incall_extension = self.create_incall_extension(row['incall'])
        entry.user_cti_profile = self.create_profile(entry.user, row['cti_profile'])

        if row['endpoint'] == 'sip':
            entry.sip = self.create_sip(row['sip'])
        elif row['endpoint'] == 'sccp':
            entry.sccp = self.create_sccp(row['sccp'])

        return entry

    def create_user(self, fields):
        return self.user_service.create(User(**fields))

    def create_voicemail(self, fields):
        if fields:
            return self.voicemail_service.create(Voicemail(**fields))

    def create_line(self, fields):
        if fields:
            return self.line_service.create(Line(**fields))

    def create_sip(self, fields):
        return self.sip_service.create(SIPEndpoint(**fields))

    def create_sccp(self, fields):
        return self.sccp_service.create(SCCPEndpoint(**fields))

    def create_extension(self, fields):
        if 'exten' in fields and 'context' in fields:
            return self.extension_service.create(Extension(**fields))

    def create_incall_extension(self, fields):
        if 'exten' in fields and 'context' in fields:
            return self.extension_service.create(Extension(exten=fields['exten'],
                                                           context=fields['context']))

    def create_profile(self, user, fields):
        if 'name' in fields:
            cti_profile_id = self.cti_profile_dao.get_id_by_name(fields['name'])
            return UserCtiProfile(user_id=user.id,
                                  cti_profile_id=cti_profile_id,
                                  enabled=fields.get('enabled'))

    def create_associations(self, entry):
        if entry.user and entry.voicemail:
            self.user_voicemail_service.associate_models(entry.user, entry.voicemail)
        if entry.line and entry.sip:
            self.line_sip_service.associate(entry.line, entry.sip)
        elif entry.line and entry.sccp:
            self.line_sccp_service.associate(entry.line, entry.sccp)
        if entry.user and entry.line:
            self.user_line_service.associate(entry.user, entry.line)
        if entry.line and entry.extension:
            self.line_extension_service.associate(entry.line, entry.extension)
        if entry.line and entry.incall_extension:
            self.associate_incall(entry.user, entry.incall_extension, entry.incall_ring_seconds)
        if entry.user and entry.user_cti_profile:
            self.associate_user_cti_profile(entry.user_cti_profile)

    def associate_incall(self, user, extension, ring_seconds=None):
        incall = Incall.user_destination(user.id,
                                         extension.id,
                                         ring_seconds=ring_seconds)
        self.incall_dao.create(incall)

    def associate_user_cti_profile(self, user_cti_profile):
        self.user_cti_profile_service.edit(user_cti_profile)





