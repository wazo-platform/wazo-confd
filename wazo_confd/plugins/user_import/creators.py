# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import abc
import random
import string

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.sccpline import SCCPLine as SCCP
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.extension import dao as extension_dao

from wazo_confd.plugins.endpoint_sip.schema import EndpointSIPSchema
from wazo_confd.plugins.extension.schema import ExtensionSchema
from wazo_confd.plugins.user.schema import UserSchema, UserSchemaNullable
from wazo_confd.plugins.voicemail.schema import VoicemailSchema

from .constants import VALID_ENDPOINT_TYPES
from .wazo_user_schema import WazoUserSchema


class Creator(metaclass=abc.ABCMeta):
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
            fields = self.schema(handle_error=False).load(fields, partial=True)

        self.update_model(fields, model)
        self.service.edit(model)

    def update_model(self, fields, model):
        for key, value in fields.items():
            setattr(model, key, value)


class UserCreator(Creator):
    schema = UserSchema
    schema_nullable = UserSchemaNullable

    def find(self, fields, tenant_uuid):
        if 'uuid' in fields:
            return self.service.get_by(uuid=fields['uuid'])

    def create(self, fields, tenant_uuid):
        if fields:
            form = self.schema_nullable(handle_error=False).load(fields)
            form['tenant_uuid'] = tenant_uuid
            return self.service.create(User(**form))


class WazoUserCreator(Creator):
    schema = WazoUserSchema

    def find(self, fields, tenant_uuid):
        pass

    def create(self, fields, tenant_uuid):
        fields = self.schema(handle_error=False).load(fields)
        fields['tenant_uuid'] = tenant_uuid
        # We need to have user_uuid on create, so the real create is on associate
        return fields

    def update(self, fields, model):
        fields = self.schema(handle_error=False).load(fields, partial=True)
        self.update_model(fields, model)
        self.service.update(model)

    def update_model(self, fields, model):
        model.update(fields)
        if 'email_address' in fields:
            email = (
                {'address': fields['email_address'], 'confirmed': True}
                if fields['email_address']
                else None
            )
            model['emails'] = [email] if email else []


class ContextCreator(Creator):
    def find(self, fields, tenant_uuid):
        name = fields.get('context')
        if name:
            return self.service.get_by(tenant_uuids=[tenant_uuid], name=name)

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

    def update(self, fields, model):
        fields = self.schema(handle_error=False).load(fields, partial=True)
        self.update_model(fields, model)
        self.service.edit(model, None)

    def create(self, fields, tenant_uuid):
        number = fields.get('number')
        context = fields.get('context')
        if number or context:
            form = self.schema(handle_error=False).load(fields)
            return self.service.create(Voicemail(**form), None)


class LineCreator(Creator):
    def find(self, fields, tenant_uuid):
        return None

    def update(self, fields, line):
        fields = dict(fields)
        if 'endpoint' in fields:
            del fields['endpoint']
            self.update_model(fields, line)
            self.service.edit(line, None)

    def create(self, fields, tenant_uuid):
        fields = dict(fields)
        context = fields.get('context')
        endpoint = fields.pop('endpoint', None)
        if context and endpoint in VALID_ENDPOINT_TYPES:
            return self.service.create(Line(**fields), None)


class SipCreator(Creator):
    schema = EndpointSIPSchema

    def __init__(self, sip_service, tenant_service, *args, **kwargs):
        super().__init__(sip_service, *args, **kwargs)
        self.tenant_service = tenant_service

    def find(self, fields, tenant_uuid):
        username = fields.get('username')
        if username:
            return self.service.find_by(username=username)

    def create(self, fields, tenant_uuid, **ignored):
        tenant = self.tenant_service.get(tenant_uuid)
        form = self._extract_form(fields, tenant)
        result = self.service.create(EndpointSIP(tenant_uuid=tenant.uuid, **form))
        self.add_templates(result, tenant)
        return result

    def _extract_form(self, fields, tenant):
        if not fields.get('username'):
            fields['username'] = self._random_string(8)
        if not fields.get('password'):
            fields['password'] = self._random_string(8)
        form = {
            'name': fields['username'],
            'auth_section_options': [[key, value] for key, value in fields.items()],
        }
        if not tenant.global_sip_template:
            raise errors.not_found('global_sip_template')

        return self.schema(handle_error=False).load(form)

    def add_templates(self, endpoint, tenant):
        endpoint.templates = [tenant.global_sip_template]
        self.service.edit(endpoint)

    def _random_string(self, length):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


class WebRTCCreator(SipCreator):
    def _extract_form(self, fields, tenant):
        if not tenant.webrtc_sip_template:
            raise errors.not_found('webrtc_sip_template')
        return super()._extract_form(fields, tenant)

    def add_templates(self, endpoint, tenant):
        endpoint.templates = [tenant.global_sip_template, tenant.webrtc_sip_template]
        self.service.edit(endpoint)


class SccpCreator(Creator):
    def find(self, fields, tenant_uuid):
        return None

    def create(self, fields, tenant_uuid):
        return self.service.create(SCCP(tenant_uuid=tenant_uuid, **fields))


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
            exten_for_user = fields.get('firstname')
            if exten_for_user:
                line_protocol = fields.get('line_protocol')
                if not line_protocol:
                    raise errors.missing('line_protocol')
                if line_protocol not in VALID_ENDPOINT_TYPES:
                    raise errors.invalid_choice('line_protocol', VALID_ENDPOINT_TYPES)

            form = self.schema(handle_error=False).load(fields)
            tenant_uuids = [tenant_uuid] if tenant_uuid is not None else None
            return self.service.create(Extension(**form), tenant_uuids=tenant_uuids)


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
        return {
            key: fields[key]
            for key in ('exten', 'context')
            if fields.get(key) is not None
        }


class IncallCreator(Creator):
    def find(self, fields, tenant_uuid):
        exten = fields.get('exten')
        context = fields.get('context')
        if exten and context:
            try:
                extension = extension_dao.get_by(
                    exten=exten, context=context, type='incall'
                )
                return self.service.get(int(extension.typeval))
            except NotFoundError:
                return None

    def create(self, fields, tenant_uuid):
        fields = self.extract_extension_fields(fields)
        if fields:
            incall = Incall(
                destination=Dialaction(action='none'), tenant_uuid=tenant_uuid
            )
            return self.service.create(incall)

    def update(self, fields, resource):
        pass

    def extract_extension_fields(self, fields):
        return {
            key: fields[key]
            for key in ('exten', 'context')
            if fields.get(key) is not None
        }


class CallPermissionCreator(Creator):
    def find(self, fields, tenant_uuid):
        names = fields.get('names')
        if names is not None:
            return [
                self.service.get_by(tenant_uuids=[tenant_uuid], name=name)
                for name in names
            ]

    def create(self, fields, tenant_uuid):
        return self.find(fields, tenant_uuid)

    def update(self, fields, resource):
        pass
