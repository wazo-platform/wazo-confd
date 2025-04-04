# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, pre_load, validates_schema
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length, Predicate, Range

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, Nested
from wazo_confd.plugins.endpoint_custom.schema import CustomSchema
from wazo_confd.plugins.endpoint_sccp.schema import SccpSchema
from wazo_confd.plugins.endpoint_sip.schema import EndpointSIPSchema
from wazo_confd.plugins.extension.schema import ExtensionSchema


class LineSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(dump_only=True)
    protocol = fields.String(dump_only=True)
    device_id = fields.String(dump_only=True)
    device_slot = fields.Integer(dump_only=True)
    provisioning_extension = fields.String(dump_only=True)

    context = fields.String(required=True)
    provisioning_code = fields.String(validate=(Predicate('isdigit'), Length(equal=6)))
    position = fields.Integer(validate=Range(min=1))
    caller_id_name = fields.String(
        allow_none=True
    )  # Validate length callerid_name + num = max(160)
    caller_id_num = fields.String(validate=Predicate('isdigit'), allow_none=True)
    registrar = fields.String(validate=Length(max=128))
    links = ListLink(Link('lines'))

    application = Nested(
        'ApplicationSchema', only=['uuid', 'name', 'links'], dump_only=True
    )
    endpoint_sip = Nested('EndpointSIPSchema')
    endpoint_sccp = Nested('SccpSchema')
    endpoint_custom = Nested('CustomSchema')
    extensions = Nested('ExtensionSchema', many=True)
    users = Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
        many=True,
        dump_only=True,
    )

    @validates_schema
    def _validate_only_one_endpoint(self, data, **kwargs):
        endpoint_sip = data.get('endpoint_sip')
        endpoint_sccp = data.get('endpoint_sccp')
        endpoint_custom = data.get('endpoint_custom')

        configured_endpoints = [
            endpoint
            for endpoint in [endpoint_sip, endpoint_sccp, endpoint_custom]
            if endpoint
        ]
        if len(configured_endpoints) > 1:
            raise ValidationError('Only one endpoint should be configured on a line')

    @validates_schema
    def _validate_multiple_caller_id(self, data, **kwargs):
        caller_id_name = data.get('caller_id_name')
        if not caller_id_name:
            return data

        endpoint_sip = data.get('endpoint_sip')
        if endpoint_sip:
            for key, value in endpoint_sip.get('endpoint_section_options'):
                if key == 'callerid':
                    raise ValidationError(
                        f'Ambiguous caller ID: line.caller_id_name = {caller_id_name} endpoint_sip.endpoint_section_options["callerid"] = {value}'
                    )

        endpoint_sccp = data.get('endpoint_sccp')
        if endpoint_sccp:
            for var, value in endpoint_sccp['options']:
                if var == 'cid_name':
                    raise ValidationError(
                        f'Ambiguous caller ID: line.caller_id_name = {caller_id_name} endpoint_sccp.options["cid_name"] = {value}'
                    )

        return data

    @pre_load
    def propagate_context(self, data, **kwargs):
        line_context = data.get('context')
        if not line_context:
            return data

        extensions = data.get('extensions', [])
        for extension in extensions:
            extension_context = extension.get('context')
            if extension_context:
                continue
            extension['context'] = line_context

        endpoint_sip = data.get('endpoint_sip')
        if endpoint_sip:
            endpoint_sip_has_context = False
            endpoint_section_options = (
                endpoint_sip.get('endpoint_section_options') or []
            )
            for key, _ in endpoint_section_options:
                if key == 'context':
                    endpoint_sip_has_context = True
                    break
            if not endpoint_sip_has_context:
                endpoint_section_options.append(
                    ['context', line_context],
                )
                endpoint_sip['endpoint_section_options'] = endpoint_section_options

        return data

    @pre_load()
    def remove_endpoints_none(self, data, **kwargs):
        for endpoint in ['endpoint_sip', 'endpoint_sccp', 'endpoint_custom']:
            try:
                if data[endpoint] is None:
                    del data[endpoint]
            except KeyError:
                pass
        return data


class LineSchemaNullable(LineSchema):
    def on_bind_field(self, field_name, field_obj):
        super().on_bind_field(field_name, field_obj)
        nullable_fields = ['provisioning_code', 'position', 'registrar']
        if field_name in nullable_fields:
            field_obj.allow_none = True


class LineListSchema(LineSchema):
    endpoint_sip = Nested(
        'EndpointSIPSchema',
        # TODO(pc-m): Is it really useful to have the username/password on the relation?
        only=[
            'uuid',
            'label',
            'name',
            'auth_section_options.username',
            'links',
        ],
        dump_only=True,
    )
    endpoint_sccp = Nested(
        'SccpSchema',
        only=['id', 'links'],
        dump_only=True,
    )
    endpoint_custom = Nested(
        'CustomSchema',
        only=['id', 'interface', 'links'],
        dump_only=True,
    )
    extensions = Nested(
        'ExtensionSchema',
        only=['id', 'exten', 'context', 'links'],
        many=True,
        dump_only=True,
    )


class UserEndpointSIPSchema(EndpointSIPSchema):
    uuid = fields.UUID()


class UserSccpSchema(SccpSchema):
    id = fields.Integer()


class UserCustomSchema(CustomSchema):
    id = fields.Integer()


class UserLineExtensionSchema(ExtensionSchema):
    id = fields.Integer(allow_none=False)


class LinePutSchema(LineSchema):
    endpoint_sip = Nested(
        'UserEndpointSIPSchema',
    )
    endpoint_sccp = Nested(
        'UserSccpSchema',
    )
    endpoint_custom = Nested(
        'UserCustomSchema',
    )
    extensions = Nested(
        'UserLineExtensionSchema',
        many=True,
    )
