# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load
from marshmallow.validate import Range
from wazo_confd.helpers.mallow import BaseSchema, Nested


class GroupUserSchema(BaseSchema):
    uuid = fields.String(required=True)
    priority = fields.Integer(validate=Range(min=0))

    @post_load
    def add_envelope(self, data, **kwargs):
        data['user'] = {'uuid': data.pop('uuid')}
        return data


class GroupUsersSchema(BaseSchema):
    users = Nested(GroupUserSchema, many=True, required=True)

    @post_load
    def set_default_priority(self, data, **kwargs):
        for priority, user in enumerate(data['users']):
            user['priority'] = user.get('priority', priority)
        return data


class GroupExtensionSchema(BaseSchema):
    exten = fields.String(required=True)
    context = fields.String(required=True)
    priority = fields.Integer(validate=Range(min=0))

    @post_load
    def add_envelope(self, data, **kwargs):
        data['extension'] = {'exten': data.pop('exten'), 'context': data.pop('context')}
        return data


class GroupExtensionsSchema(BaseSchema):
    extensions = Nested(GroupExtensionSchema, many=True, required=True)

    @post_load
    def set_default_priority(self, data, **kwargs):
        for priority, extension in enumerate(data['extensions']):
            extension['priority'] = extension.get('priority', priority)
        return data
