# -*- coding: UTF-8 -*-
# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields
from marshmallow.validate import Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.validator import EXTEN_REGEX


class ExtensionSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    exten = fields.String(validate=Regexp(EXTEN_REGEX), required=True)
    context = fields.String(required=True)
    commented = fields.Boolean(attribute='legacy_commented')
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
                          only=['id', 'links'],
                          many=True,
                          dump_only=True)
    outcall = fields.Nested('OutcallSchema',
                            only=['id', 'name', 'links'],
                            dump_only=True)
