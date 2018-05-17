# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields, post_dump
from marshmallow.validate import Length

from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink


class CallPickupSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    description = fields.String(allow_none=True)
    enabled = StrictBoolean()
    links = ListLink(Link('callpickups'))

    user_interceptors = fields.Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname'],
        many=True,
        dump_only=True
    )
    user_targets = fields.Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname'],
        many=True,
        dump_only=True
    )

    @post_dump
    def wrap_users(self, data):
        interceptor_users = data.pop('user_interceptors', [])
        target_users = data.pop('user_targets', [])

        if not self.only or 'user_interceptors' in self.only:
            data['interceptors'] = {'users': interceptor_users}
        if not self.only or 'user_target' in self.only:
            data['targets'] = {'users': target_users}

        return data
