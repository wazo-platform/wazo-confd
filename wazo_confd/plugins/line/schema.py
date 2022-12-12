# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, validates_schema, pre_load
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
    extensions = Nested('ExtensionSchema', many=True)
    users = Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
        many=True,
        dump_only=True,
    )

    @validates_schema
    def _validate_only_one_endpoint(self, data, **kwargs):
        nb_endpoint = 0
        if data.get('endpoint_sip'):
            nb_endpoint += 1
        if data.get('endpoint_sccp'):
            nb_endpoint += 1
        if data.get('endpoint_custom'):
            nb_endpoint += 1

        if nb_endpoint > 1:
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

    @pre_load
    def populate_missing_context(self, data, **kwargs):
        extensions = data.get('extensions', [])
        for ext in extensions:
            if 'context' not in ext:
                ext['context'] = data.get('context')

        return data


class LineSchemaNullable(LineSchema):
    def on_bind_field(self, field_name, field_obj):
        super().on_bind_field(field_name, field_obj)
        nullable_fields = ['provisioning_code', 'position', 'registrar']
        if field_name in nullable_fields:
            field_obj.allow_none = True


class LineListSchema(LineSchema):
    extensions = Nested(
        'ExtensionSchema',
        only=['id', 'exten', 'context', 'links'],
        many=True,
    )
    endpoint_sip = Nested(
        'EndpointSIPSchema',
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