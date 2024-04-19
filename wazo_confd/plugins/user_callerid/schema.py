# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo_confd.helpers.mallow import BaseSchema


class UserCallerIDSchema(BaseSchema):
    number = fields.String(dump_only=True)
    type = fields.String(dump_only=True)
