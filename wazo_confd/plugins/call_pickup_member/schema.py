# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo_confd.helpers.mallow import BaseSchema, Nested


class CallPickupInterceptorGroupSchema(BaseSchema):
    id = fields.Integer(required=True)


class CallPickupInterceptorGroupsSchema(BaseSchema):
    groups = Nested(CallPickupInterceptorGroupSchema, many=True, required=True)


class CallPickupTargetGroupSchema(BaseSchema):
    id = fields.Integer(required=True)


class CallPickupTargetGroupsSchema(BaseSchema):
    groups = Nested(CallPickupTargetGroupSchema, many=True, required=True)


class CallPickupInterceptorUserSchema(BaseSchema):
    uuid = fields.String(required=True)


class CallPickupInterceptorUsersSchema(BaseSchema):
    users = Nested(CallPickupInterceptorUserSchema, many=True, required=True)


class CallPickupTargetUserSchema(BaseSchema):
    uuid = fields.String(required=True)


class CallPickupTargetUsersSchema(BaseSchema):
    users = Nested(CallPickupTargetUserSchema, many=True, required=True)
