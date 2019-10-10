# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import EXCLUDE, fields, post_load
from marshmallow.validate import Range

from wazo_confd.helpers.mallow import BaseSchema


class CallFilterRecipientUserSchema(BaseSchema):
    uuid = fields.String(required=True)
    timeout = fields.Integer(validate=Range(min=0), allow_none=True, missing=None)

    @post_load
    def add_envelope(self, data):
        data['user'] = {'uuid': data.pop('uuid')}
        return data


class CallFilterRecipientUsersSchema(BaseSchema):
    users = fields.Nested(
        CallFilterRecipientUserSchema, many=True, required=True, unknown=EXCLUDE
    )


class CallFilterSurrogateUserSchema(BaseSchema):
    uuid = fields.String(required=True)

    @post_load
    def add_envelope(self, data):
        data['user'] = {'uuid': data.pop('uuid')}
        return data


class CallFilterSurrogateUsersSchema(BaseSchema):
    users = fields.Nested(
        CallFilterSurrogateUserSchema, many=True, required=True, unknown=EXCLUDE
    )
