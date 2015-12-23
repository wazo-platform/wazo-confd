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


import abc

from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.exception import NotFoundError

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.resources.user_cti_profile.model import UserCtiProfile
from xivo_dao.resources.user_voicemail.model import UserVoicemail


class Associator(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, service):
        self.service = service

    @abc.abstractmethod
    def associate(self, entry):
        return

    @abc.abstractmethod
    def update(self, entry):
        return


class LineAssociator(Associator):

    def associate(self, entry):
        user = entry.get_resource('user')
        line = entry.get_resource('line')
        if user and line:
            self.service.associate(user, line)

    def update(self, entry):
        user = entry.get_resource('user')
        line = entry.get_resource('line')
        if user and line and not self.associated(user, line):
            self.service.associate(user, line)

    def associated(self, user, line):
        return self.service.find_by(user_id=user.id, line_id=line.id) is not None


class ExtensionAssociator(Associator):

    def associate(self, entry):
        line = entry.get_resource('line')
        extension = entry.get_resource('extension')
        if line and extension:
            self.service.associate(line, extension)

    def update(self, entry):
        line = entry.get_resource('line')
        extension = entry.get_resource('extension')
        if line and extension and not self.associated(line, extension):
            self.service.associate(line, extension)

    def associated(self, line, extension):
        try:
            self.service.get(line, extension)
        except NotFoundError:
            return False
        return True


class SipAssociator(Associator):

    def associate(self, entry):
        line = entry.get_resource('line')
        sip = entry.get_resource('sip')
        if line and sip:
            self.service.associate(line, sip)

    def update(self, entry):
        line = entry.get_resource('line')
        sip = entry.get_resource('sip')
        if line and sip and not line.is_associated_with(sip):
                self.service.associate(line, sip)


class SccpAssociator(Associator):

    def associate(self, entry):
        line = entry.get_resource('line')
        sccp = entry.get_resource('sccp')
        if line and sccp:
            self.service.associate(line, sccp)

    def update(self, entry):
        line = entry.get_resource('line')
        sccp = entry.get_resource('sccp')
        if line and sccp and not line.is_associated_with(sccp):
                self.service.associate(line, sccp)


class VoicemailAssociator(Associator):

    def associate(self, entry):
        user = entry.get_resource('user')
        voicemail = entry.get_resource('voicemail')
        if user and voicemail:
            self.create_and_associate(user, voicemail)

    def create_and_associate(self, user, voicemail):
        association = UserVoicemail(user_id=user.id,
                                    voicemail_id=voicemail.id)
        self.service.associate(association)

    def update(self, entry):
        user = entry.get_resource('user')
        voicemail = entry.get_resource('voicemail')
        if user and voicemail and not self.associated(user, voicemail):
            self.create_and_associate(user, voicemail)

    def associated(self, user, voicemail):
        return self.service.find_by(user_id=user.id, voicemail_id=voicemail.id) is not None


class CtiProfileAssociator(Associator):

    def __init__(self, service, dao):
        self.service = service
        self.dao = dao

    def associate(self, entry):
        cti_profile = entry.get_resource('cti_profile')
        if cti_profile:
            self.associate_profile(entry)

    def update(self, entry):
        self.associate(entry)

    def associate_profile(self, entry):
        user = entry.get_resource('user')
        name = entry.extract_field('cti_profile', 'name')
        cti_profile_id = self.dao.get_id_by_name(name)
        association = UserCtiProfile(user_id=user.id,
                                     cti_profile_id=cti_profile_id,
                                     enabled=entry.extract_field('cti_profile', 'enabled'))
        self.service.edit(association)


class IncallAssociator(Associator):

    def associate(self, entry):
        line = entry.get_resource('line')
        incall = entry.get_resource('incall')
        if line and incall:
            self.service.associate(line, incall)
            self.update_ring_seconds(entry)

    def update_ring_seconds(self, entry):
        ring_seconds = entry.extract_field('incall', 'ring_seconds')
        if ring_seconds:
            user = entry.get_resource('user')
            (Session.query(Dialaction)
             .filter_by(event='answer',
                        category='incall',
                        action='user',
                        actionarg1=str(user.id))
             .update({'actionarg2': str(ring_seconds)}))

    def update(self, entry):
        line = entry.get_resource('line')
        incall = entry.get_resource('incall')
        if line and incall and not self.associated(line, incall):
            self.service.associate(line, incall)
            self.update_ring_seconds(entry)

    def associated(self, line, extension):
        try:
            self.service.get(line, extension)
        except NotFoundError:
            return False
        return True
