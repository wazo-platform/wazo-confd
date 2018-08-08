# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import abc

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.sccpline import SCCPLine as SCCP
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.usersip import UserSIP as SIP
from xivo_dao.alchemy.voicemail import Voicemail

from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd.plugins.endpoint_sip.schema import SipSchema, SipSchemaNullable
from xivo_confd.plugins.extension.schema import ExtensionSchema
from xivo_confd.plugins.user.schema import UserSchema, UserSchemaNullable
from xivo_confd.plugins.voicemail.schema import VoicemailSchema

from .wazo_user_schema import WazoUserSchema


class Creator(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, service):
        self.service = service

    @abc.abstractmethod
    def find(self, fields, tenant_uuid):
        pass

    @abc.abstractmethod
    def create(self, fields, tenant_uuid):
        pass

    def update(self, fields, model):
        if getattr(self, 'schema', False):
            fields = self.schema(handle_error=False, strict=True).load(fields, partial=True).data

        self.update_model(fields, model)
        self.service.edit(model)

    def update_model(self, fields, model):
        for key, value in fields.iteritems():
            setattr(model, key, value)


class UserCreator(Creator):

    schema = UserSchema
    schema_nullable = UserSchemaNullable

    def find(self, fields, tenant_uuid):
        if 'uuid' in fields:
            return self.service.get_by(uuid=fields['uuid'])

    def create(self, fields, tenant_uuid):
        if fields:
            form = self.schema_nullable(handle_error=False, strict=True).load(fields).data
            form['tenant_uuid'] = tenant_uuid
            return self.service.create(User(**form))


class WazoUserCreator(Creator):

    schema = WazoUserSchema

    def find(self, fields, tenant_uuid):
        pass

    def create(self, fields, tenant_uuid):
        fields = self.schema(handle_error=False, strict=True).load(fields).data
        # We need to have user_uuid on create, so the real create is on associate
        return fields

    def update(self, fields, model):
        fields = self.schema(handle_error=False, strict=True).load(fields, partial=True).data
        self.update_model(fields, model)
        self.service.update(model)

    def update_model(self, fields, model):
        model.update(fields)
        if 'email_address' in fields:
            email = {'address': fields['email_address'], 'confirmed': True} if fields['email_address'] else None
            model['emails'] = [email] if email else []


class EntityCreator(Creator):

    def find(self, fields, tenant_uuid):
        entity_id = fields.get('id')
        if entity_id:
            return self.service.get_by(id=entity_id)

    def create(self, fields, tenant_uuid):
        return None

    def update(self, fields, model):
        pass


class VoicemailCreator(Creator):

    schema = VoicemailSchema

    def find(self, fields, tenant_uuid):
        number = fields.get('number')
        context = fields.get('context')
        if number or context:
            return self.service.dao.find_by(number=number, context=context)

    def create(self, fields, tenant_uuid):
        number = fields.get('number')
        context = fields.get('context')
        if number or context:
            form = self.schema(handle_error=False, strict=True).load(fields).data
            return self.service.create(Voicemail(**form))


class LineCreator(Creator):

    def find(self, fields, tenant_uuid):
        return None

    def update(self, fields, line):
        fields = dict(fields)
        if 'endpoint' in fields:
            del fields['endpoint']
            self.update_model(fields, line)
            self.service.edit(line)

    def create(self, fields, tenant_uuid):
        fields = dict(fields)
        context = fields.get('context')
        endpoint = fields.pop('endpoint', None)
        if context and endpoint in ('sip', 'sccp'):
            return self.service.create(Line(**fields))


class SipCreator(Creator):

    schema = SipSchema
    schema_nullable = SipSchemaNullable

    def find(self, fields, tenant_uuid):
        name = fields.get('username')
        if name:
            return self.service.find_by(name=name)

    def create(self, fields, tenant_uuid):
        form = self.schema_nullable(handle_error=False, strict=True).load(fields).data
        return self.service.create(SIP(**form))


class SccpCreator(Creator):

    def find(self, fields, tenant_uuid):
        return None

    def create(self, fields, tenant_uuid):
        return self.service.create(SCCP(**fields))


class ExtensionCreator(Creator):

    schema = ExtensionSchema

    def find(self, fields, tenant_uuid):
        exten = fields.get('exten')
        context = fields.get('context')
        if exten and context:
            try:
                return self.service.dao.get_by(exten=exten, context=context)
            except NotFoundError:
                return None

    def create(self, fields, tenant_uuid):
        exten = fields.get('exten')
        context = fields.get('context')
        if exten and context:
            form = self.schema(handle_error=False, strict=True).load(fields).data
            tenant_uuids = [tenant_uuid] if tenant_uuid is not None else None
            return self.service.create(Extension(**form), tenant_uuids=tenant_uuids)


class CtiProfileCreator(Creator):

    def __init__(self, dao):
        self.dao = dao

    def find(self, fields, tenant_uuid):
        name = fields.get('name')
        if name:
            try:
                cti_profile_id = self.dao.get_id_by_name(name)
                return self.dao.get(cti_profile_id)
            except NotFoundError:
                return None

    def update(self, fields, resource):
        pass

    def create(self, fields, tenant_uuid):
        name = fields.get('name')
        if name:
            cti_profile_id = self.dao.get_id_by_name(name)
            return self.dao.get(cti_profile_id)


class ExtensionIncallCreator(Creator):

    def find(self, fields, tenant_uuid):
        exten = fields.get('exten')
        context = fields.get('context')
        if exten and context:
            try:
                return self.service.get_by(exten=exten, context=context)
            except NotFoundError:
                return None

    def create(self, fields, tenant_uuid):
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


class IncallCreator(Creator):

    def find(self, fields, tenant_uuid):
        exten = fields.get('exten')
        context = fields.get('context')
        if exten and context:
            try:
                extension = extension_dao.get_by(exten=exten, context=context, type='incall')
                return self.service.get(int(extension.typeval))
            except NotFoundError:
                return None

    def create(self, fields, tenant_uuid):
        fields = self.extract_extension_fields(fields)
        if fields:
            incall = Incall(destination=Dialaction(action='none'), tenant_uuid=tenant_uuid)
            return self.service.create(incall)

    def update(self, fields, resource):
        pass

    def extract_extension_fields(self, fields):
        return {key: fields[key]
                for key in ('exten', 'context')
                if fields.get(key) is not None}


class CallPermissionCreator(Creator):

    def find(self, fields, tenant_uuid):
        names = fields.get('names')
        if names is not None:
            return [self.service.get_by(name=name) for name in names]

    def create(self, fields, tenant_uuid):
        return self.find(fields, tenant_uuid)

    def update(self, fields, resource):
        pass
