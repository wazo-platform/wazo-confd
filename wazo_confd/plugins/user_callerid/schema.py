# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_dump

from wazo_confd.helpers.mallow import BaseSchema


class UserCallerIDSchema(BaseSchema):
    number = fields.String(dump_only=True)
    type = fields.String(dump_only=True)

    @post_dump
    def omit_number_for_anonymous(self, data, **kwargs):
        if data.get('type') == 'anonymous':
            data.pop('number', None)
        return data
