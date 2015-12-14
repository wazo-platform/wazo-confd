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

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.usersip import UserSIP as SIP
from xivo_dao.alchemy.sccpline import SCCPLine as SCCP
from xivo_dao.resources.voicemail.model import Voicemail

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.resources.extension.model import Extension
from xivo_dao.resources.user_cti_profile.model import UserCtiProfile
from xivo_dao.resources.incall.model import Incall
from xivo_dao.resources.user_voicemail.model import UserVoicemail


class Creator(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, service):
        self.service = service

    @abc.abstractmethod
    def create(self, fields):
        pass


class UserCreator(Creator):

    def create(self, fields):
        if fields:
            return self.service.create(User(**fields))


class VoicemailCreator(Creator):

    def create(self, fields):
        if fields:
            return self.service.create(Voicemail(**fields))


class LineCreator(Creator):

    def create(self, fields):
        fields = dict(fields)
        endpoint = fields.pop('endpoint', None)
        if 'context' in fields and endpoint in ('sip', 'sccp'):
            return self.service.create(Line(**fields))


class SipCreator(Creator):

    def create(self, fields):
        return self.service.create(SIP(**fields))


class SccpCreator(Creator):

    def create(self, fields):
        return self.service.create(SCCP(**fields))


class ExtensionCreator(Creator):

    def create(self, fields):
        if 'exten' in fields and 'context' in fields:
            return self.service.create(Extension(**fields))


class CtiProfileCreator(Creator):

    def __init__(self, dao):
        self.dao = dao

    def create(self, fields):
        if fields:
            cti_profile_id = self.dao.get_id_by_name(fields['name'])
            return self.dao.get(cti_profile_id)


class IncallCreator(Creator):

    def __init__(self, service):
        self.service = service

    def create(self, fields):
        if fields:
            extension = Extension(exten=fields['exten'],
                                  context=fields['context'])
            return self.service.create(extension)


class Associator(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def associate(self, entry):
        return


class BaseAssociator(Associator):

    def __init__(self, left, right, service):
        self.left = left
        self.right = right
        self.service = service

    def associate(self, entry):
        left_resource = entry.get_resource(self.left)
        right_resource = entry.get_resource(self.right)
        if left_resource and right_resource:
            self.service.associate(left_resource, right_resource)


class VoicemailAssociator(Associator):

    def __init__(self, service):
        self.service = service

    def associate(self, entry):
        user = entry.get_resource('user')
        voicemail = entry.get_resource('voicemail')
        if user and voicemail:
            association = UserVoicemail(user_id=user.id,
                                        voicemail_id=voicemail.id)
            self.service.associate(association)


class CtiProfileAssociator(Associator):

    def __init__(self, service):
        self.service = service

    def associate(self, entry):
        user = entry.get_resource('user')
        cti_profile = entry.get_resource('cti_profile')
        if user and cti_profile:
            association = UserCtiProfile(user_id=user.id,
                                         cti_profile_id=cti_profile.id,
                                         enabled=entry.extract_field('cti_profile', 'enabled'))
            self.service.edit(association)


class IncallAssociator(Associator):

    def __init__(self, dao):
        self.dao = dao

    def associate(self, entry):
        user = entry.get_resource('user')
        extension = entry.get_resource('incall')
        if user and extension:
            incall = Incall.user_destination(user.id,
                                             extension.id,
                                             entry.extract_field('incall', 'ring_seconds'))
            self.dao.create(incall)
