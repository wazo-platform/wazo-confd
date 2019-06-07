# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load
from marshmallow.validate import Range
from xivo_confd.helpers.mallow import BaseSchema


class GroupUserSchema(BaseSchema):
    uuid = fields.String(required=True)
    priority = fields.Integer(validate=Range(min=0))

    @post_load
    def add_envelope(self, data):
        data['user'] = {'uuid': data.pop('uuid')}
        return data


class GroupUsersSchema(BaseSchema):
    users = fields.Nested(GroupUserSchema, many=True, required=True)

    @post_load
    def set_default_priority(self, data):
        for priority, user in enumerate(data['users']):
            user['priority'] = user.get('priority', priority)
        return data


class GroupExtensionSchema(BaseSchema):
    exten = fields.String(required=True)
    context = fields.String(required=True)
    priority = fields.Integer(validate=Range(min=0))

    @post_load
    def add_envelope(self, data):
        data['extension'] = {'exten': data.pop('exten'),
                             'context': data.pop('context')}
        return data


class GroupExtensionsSchema(BaseSchema):
    extensions = fields.Nested(GroupExtensionSchema, many=True, required=True)

    @post_load
    def set_default_priority(self, data):
        for priority, extension in enumerate(data['extensions']):
            extension['priority'] = extension.get('priority', priority)
        return data
