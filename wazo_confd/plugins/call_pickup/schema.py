# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_dump
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink, Nested


class CallPickupSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    description = fields.String(allow_none=True)
    enabled = StrictBoolean()
    links = ListLink(Link('callpickups'))

    group_interceptors = Nested(
        'GroupSchema', only=['id', 'name', 'label'], many=True, dump_only=True
    )
    group_targets = Nested(
        'GroupSchema', only=['id', 'name', 'label'], many=True, dump_only=True
    )
    user_interceptors = Nested(
        'UserSchema', only=['uuid', 'firstname', 'lastname'], many=True, dump_only=True
    )
    user_targets = Nested(
        'UserSchema', only=['uuid', 'firstname', 'lastname'], many=True, dump_only=True
    )

    @post_dump
    def wrap_users(self, data, **kwargs):
        interceptor_groups = data.pop('group_interceptors', [])
        interceptor_users = data.pop('user_interceptors', [])
        target_groups = data.pop('group_targets', [])
        target_users = data.pop('user_targets', [])

        if not self.only or 'interceptors' in self.only:
            data['interceptors'] = {
                'groups': interceptor_groups,
                'users': interceptor_users,
            }
        if not self.only or 'targets' in self.only:
            data['targets'] = {'groups': target_groups, 'users': target_users}

        return data
