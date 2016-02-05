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

import abc

from xivo_dao.helpers.exception import NotFoundError

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.usersip import UserSIP as SIP
from xivo_dao.alchemy.sccpline import SCCPLine as SCCP
from xivo_dao.resources.voicemail.model import Voicemail

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.resources.extension.model import Extension


class Creator(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, service):
        self.service = service

    @abc.abstractmethod
    def find(self, fields):
        pass

    @abc.abstractmethod
    def create(self, fields):
        pass

    def update(self, fields, model):
        self.update_model(fields, model)
        self.service.edit(model)

    def update_model(self, fields, model):
        for key, value in fields.iteritems():
            setattr(model, key, value)


class UserCreator(Creator):

    def find(self, fields):
        if 'uuid' in fields:
            return self.service.get_by(uuid=fields['uuid'])

    def create(self, fields):
        if fields:
            return self.service.create(User(**fields))


class VoicemailCreator(Creator):

    def find(self, fields):
        number = fields.get('number')
        context = fields.get('context')
        if number or context:
            try:
                return self.service.dao.get_by_number_context(number, context)
            except NotFoundError:
                return None

    def create(self, fields):
        number = fields.get('number')
        context = fields.get('context')
        if number or context:
            return self.service.create(Voicemail(**fields))


class LineCreator(Creator):

    def find(self, fields):
        return None

    def update(self, fields, line):
        fields = dict(fields)
        if 'endpoint' in fields:
            del fields['endpoint']
            self.update_model(fields, line)
            self.service.edit(line)

    def create(self, fields):
        fields = dict(fields)
        context = fields.get('context')
        endpoint = fields.pop('endpoint', None)
        if context and endpoint in ('sip', 'sccp'):
            return self.service.create(Line(**fields))


class SipCreator(Creator):

    def find(self, fields):
        name = fields.get('name')
        if name:
            return self.service.find_by(name=name)

    def create(self, fields):
        return self.service.create(SIP(**fields))


class SccpCreator(Creator):

    def find(self, fields):
        return None

    def create(self, fields):
        return self.service.create(SCCP(**fields))


class ExtensionCreator(Creator):

    def find(self, fields):
        exten = fields.get('exten')
        context = fields.get('context')
        if exten and context:
            try:
                return self.service.dao.get_by_exten_context(exten, context)
            except NotFoundError:
                return None

    def create(self, fields):
        exten = fields.get('exten')
        context = fields.get('context')
        if exten and context:
            return self.service.create(Extension(**fields))


class CtiProfileCreator(Creator):

    def __init__(self, dao):
        self.dao = dao

    def find(self, fields):
        name = fields.get('name')
        if name:
            try:
                cti_profile_id = self.dao.get_id_by_name(name)
                return self.dao.get(cti_profile_id)
            except NotFoundError:
                return None

    def update(self, fields, resource):
        pass

    def create(self, fields):
        name = fields.get('name')
        if name:
            cti_profile_id = self.dao.get_id_by_name(name)
            return self.dao.get(cti_profile_id)


class IncallCreator(Creator):

    def find(self, fields):
        exten = fields.get('exten')
        context = fields.get('context')
        if exten and context:
            try:
                return self.service.dao.get_by_exten_context(exten, context)
            except NotFoundError:
                return None

    def create(self, fields):
        fields = self.extract_extension_fields(fields)
        if fields:
            extension = Extension(**fields)
            return self.service.create(extension)

    def update(self, fields, resource):
        extension_fields = self.extract_extension_fields(fields)
        self.update_model(extension_fields, resource)
        self.service.edit(resource)

    def extract_extension_fields(self, fields):
        return {key: fields[key]
                for key in ('exten', 'context')
                if fields.get(key) is not None}


class CallPermissionCreator(Creator):

    def __init__(self, dao):
        self.dao = dao

    def find(self, fields):
        names = fields.get('names')
        if names is not None:
            return [self.dao.get_by(name=name) for name in names]

    def create(self, fields):
        return self.find(fields)

    def update(self, fields, resource):
        pass
