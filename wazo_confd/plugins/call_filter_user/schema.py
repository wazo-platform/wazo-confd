# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load
from marshmallow.validate import Range

from wazo_confd.helpers.mallow import BaseSchema, Nested


class CallFilterRecipientUserSchema(BaseSchema):
    uuid = fields.String(required=True)
    timeout = fields.Integer(validate=Range(min=0), allow_none=True, missing=None)

    @post_load
    def add_envelope(self, data, **kwargs):
        data['user'] = {'uuid': data.pop('uuid')}
        return data


class CallFilterRecipientUsersSchema(BaseSchema):
    users = Nested(CallFilterRecipientUserSchema, many=True, required=True)


class CallFilterSurrogateUserSchema(BaseSchema):
    uuid = fields.String(required=True)

    @post_load
    def add_envelope(self, data, **kwargs):
        data['user'] = {'uuid': data.pop('uuid')}
        return data


class CallFilterSurrogateUsersSchema(BaseSchema):
    users = Nested(CallFilterSurrogateUserSchema, many=True, required=True)
