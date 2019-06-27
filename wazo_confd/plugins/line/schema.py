# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length, Predicate, Range

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink


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
    caller_id_name = fields.String(allow_none=True)  # Validate length callerid_name + num = max(160)
    caller_id_num = fields.String(validate=Predicate('isdigit'), allow_none=True)
    registrar = fields.String(validate=Length(max=128))
    links = ListLink(Link('lines'))

    application = fields.Nested('ApplicationSchema', only=['uuid', 'name', 'links'], dump_only=True)
    endpoint_sip = fields.Nested('SipSchema', only=['id', 'username', 'links'], dump_only=True)
    endpoint_sccp = fields.Nested('SccpSchema', only=['id', 'links'], dump_only=True)
    endpoint_custom = fields.Nested('CustomSchema', only=['id', 'interface', 'links'], dump_only=True)
    extensions = fields.Nested(
        'ExtensionSchema',
        only=['id', 'exten', 'context', 'links'],
        many=True,
        dump_only=True,
    )
    users = fields.Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
        many=True,
        dump_only=True,
    )


class LineSchemaNullable(LineSchema):

    def on_bind_field(self, field_name, field_obj):
        super(LineSchemaNullable, self).on_bind_field(field_name, field_obj)
        nullable_fields = ['provisioning_code', 'position', 'registrar']
        if field_name in nullable_fields:
            field_obj.allow_none = True
