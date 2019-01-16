# -*- coding: utf-8 -*-
# Copyright (C) 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length, Predicate, Range

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class ConferenceSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(allow_none=True, validate=Length(max=128))
    preprocess_subroutine = fields.String(allow_none=True, validate=Length(max=39))
    max_users = fields.Integer(validate=Range(min=0))
    record = fields.Boolean()
    pin = fields.String(allow_none=True, validate=(Length(max=80), Predicate('isdigit')))
    admin_pin = fields.String(allow_none=True, validate=(Length(max=80), Predicate('isdigit')))
    quiet_join_leave = fields.Boolean()
    announce_join_leave = fields.Boolean()
    announce_user_count = fields.Boolean()
    announce_only_user = fields.Boolean()
    music_on_hold = fields.String(allow_none=True, validate=Length(max=128))
    links = ListLink(Link('conferences'))

    extensions = fields.Nested('ExtensionSchema',
                               only=['id', 'exten', 'context', 'links'],
                               many=True,
                               dump_only=True)
    incalls = fields.Nested('IncallSchema',
                            only=['id',
                                  'extensions',
                                  'links'],
                            many=True,
                            dump_only=True)
