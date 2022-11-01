# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, validates_schema
from marshmallow.validate import Length, Predicate, Range
from marshmallow.exceptions import ValidationError

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, Nested


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
    extensions = Nested(
        'ExtensionSchema',
        only=['id', 'exten', 'context', 'links'],
        many=True,
        dump_only=True,
    )
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
                        'Ambiguous caller ID: line.caller_id_name = {} endpoint_sip.endpoint_section_options["callerid"] = {}',
                        caller_id_name,
                        value,
                    )

        endpoint_sccp = data.get('endpoint_sccp')
        if endpoint_sccp:
            for var, value in endpoint_sccp['options']:
                if var == 'cid_name':
                    raise ValidationError(
                        'Ambiguous caller ID: line.caller_id_name = {} endpoint_sccp.options["cid_name"] = {}',
                        caller_id_name,
                        value,
                    )

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


class LinePutSchema(LineListSchema):
    pass
