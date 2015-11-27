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
from xivo_dao.resources.user_voicemail.model import UserVoicemail
from xivo_dao.resources.line_extension.model import LineExtension
from xivo_dao.resources.user_line.model import UserLine
from xivo_dao.resources.voicemail.model import Voicemail
from xivo_dao.resources.incall.model import Incall

from xivo_dao.helpers.exception import ServiceError


class Entry(object):

    def __init__(self, row_number, user):
        self.row_number = row_number
        self.user = user
        self.voicemail = None
        self.line = None
        self.sip = None
        self.extension = None
        self.incall_extension = None
        self.incall_ring_seconds = None

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


class ImportService(object):

    def __init__(self, user_service, voicemail_service, user_voicemail_service,
                 line_service, sip_service, sccp_service, line_sip_service,
                 line_sccp_service, extension_service, line_extension_service,
                 user_line_service, incall_dao):
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

    def import_rows(self, parser):
        created = []
        errors = []

        for position, row in enumerate(parser, 1):
            try:
                entry = self.create_entry(position, row.parse())
                self.create_associations(entry)
                created.append(entry)
            except ServiceError as e:
                errors.append(row.format_error(position, e))

        return created, errors

    def create_entry(self, position, row):
        user = self.create_user(row['user'])
        entry = Entry(position, user)

        if 'voicemail' in row:
            entry.voicemail = self.create_voicemail(row['voicemail'])
        if 'line' in row:
            entry.line = self.create_line(row['line'])
        if 'sip' in row:
            entry.sip = self.create_sip(row['sip'])
        if 'sccp' in row:
            entry.sccp = self.create_sccp(row['sccp'])
        if 'extension' in row:
            entry.extension = self.create_extension(row['extension'])
        if 'incall' in row:
            entry.incall_extension = self.create_incall_extension(row['incall'])
            entry.incall_ring_seconds = row['incall']['ring_seconds']

        return entry

    def create_user(self, fields):
        user = User(**fields)
        return self.user_service.create(user)

    def create_voicemail(self, fields):
        voicemail = Voicemail(**fields)
        voicemail = self.voicemail_service.create(voicemail)
        return voicemail

    def create_line(self, fields):
        line = Line(**fields)
        return self.line_service.create(line)

    def create_sip(self, fields):
        sip = SIPEndpoint(**fields)
        sip = self.sip_service.create(sip)
        return sip

    def create_sccp(self, fields):
        sccp = SCCPEndpoint(**fields)
        sccp = self.sccp_service.create(sccp)
        return sccp

    def create_extension(self, fields):
        extension = Extension(**fields)
        extension = self.extension_service.create(extension)
        return extension

    def create_incall_extension(self, fields):
        extension = Extension(exten=fields['exten'],
                              context=fields['context'])
        return self.extension_service.create(extension)

    def create_associations(self, entry):
        if entry.user and entry.voicemail:
            self.associate_user_voicemail(entry)
        if entry.line and entry.sip:
            self.associate_line_sip(entry)
        elif entry.line and entry.sccp:
            self.associate_line_sccp(entry)
        if entry.user and entry.line:
            self.associate_user_line(entry)
        if entry.line and entry.extension:
            self.associate_line_extension(entry)
        if entry.line and entry.incall_extension:
            self.associate_incall(entry)

    def associate_user_voicemail(self, entry):
        user_voicemail = UserVoicemail(user_id=entry.user_id,
                                       voicemail_id=entry.voicemail_id)
        self.user_voicemail_service.associate(user_voicemail)

    def associate_line_sip(self, entry):
        self.line_sip_service.associate(entry.line, entry.sip)

    def associate_line_sccp(self, entry):
        self.line_sccp_service.associate(entry.line, entry.sccp)

    def associate_line_extension(self, entry):
        line_extension = LineExtension(line_id=entry.line_id,
                                       extension_id=entry.extension_id)
        self.line_extension_service.associate(line_extension)

    def associate_user_line(self, entry):
        user_line = UserLine(user_id=entry.user_id,
                             line_id=entry.line_id)
        self.user_line_service.associate(user_line)

    def associate_incall(self, entry):
        incall = Incall.user_destination(entry.user_id,
                                         entry.incall_extension_id,
                                         ring_seconds=entry.incall_ring_seconds)
        self.incall_dao.create(incall)
