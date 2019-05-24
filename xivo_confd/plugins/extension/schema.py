# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class ExtensionSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    exten = fields.String(validate=Length(max=40), required=True)
    context = fields.String(required=True)
    commented = fields.Boolean(attribute='legacy_commented')
    enabled = fields.Boolean()
    links = ListLink(Link('extensions'))

    conference = fields.Nested('ConferenceSchema',
                               only=['id', 'name', 'links'],
                               dump_only=True)
    parking_lot = fields.Nested('ParkingLotSchema',
                                only=['id', 'name', 'links'],
                                dump_only=True)
    group = fields.Nested('GroupSchema',
                          only=['id', 'name', 'links'],
                          dump_only=True)
    incall = fields.Nested('IncallSchema',
                           only=['id', 'links'],
                           dump_only=True)
    lines = fields.Nested('LineSchema',
                          only=['id', 'name', 'links'],
                          many=True,
                          dump_only=True)
    outcall = fields.Nested('OutcallSchema',
                            only=['id', 'name', 'links'],
                            dump_only=True)
    queue = fields.Nested('QueueSchema',
                          only=['id', 'name', 'label', 'links'],
                          dump_only=True)
