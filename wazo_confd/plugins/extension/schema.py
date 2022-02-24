# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, Nested


class ExtensionSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    exten = fields.String(validate=Length(max=40), required=True)
    context = fields.String(required=True)
    commented = fields.Boolean(attribute='legacy_commented')
    enabled = fields.Boolean()
    links = ListLink(Link('extensions'))

    conference = Nested(
        'ConferenceSchema', only=['id', 'name', 'links'], dump_only=True
    )
    parking_lot = Nested(
        'ParkingLotSchema', only=['id', 'name', 'links'], dump_only=True
    )
    group = Nested('GroupSchema', only=['uuid', 'id', 'name', 'links'], dump_only=True)
    incall = Nested('IncallSchema', only=['id', 'links'], dump_only=True)
    lines = Nested(
        'LineSchema', only=['id', 'name', 'links'], many=True, dump_only=True
    )
    outcall = Nested('OutcallSchema', only=['id', 'name', 'links'], dump_only=True)
    queue = Nested('QueueSchema', only=['id', 'name', 'label', 'links'], dump_only=True)
