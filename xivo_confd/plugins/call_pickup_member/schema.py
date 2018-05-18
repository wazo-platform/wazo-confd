# -*- coding: UTF-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields

from xivo_confd.helpers.mallow import BaseSchema


class CallPickupInterceptorGroupSchema(BaseSchema):
    id = fields.Integer(required=True)


class CallPickupInterceptorGroupsSchema(BaseSchema):
    groups = fields.Nested(CallPickupInterceptorGroupSchema, many=True, required=True)


class CallPickupTargetGroupSchema(BaseSchema):
    id = fields.Integer(required=True)


class CallPickupTargetGroupsSchema(BaseSchema):
    groups = fields.Nested(CallPickupTargetGroupSchema, many=True, required=True)


class CallPickupInterceptorUserSchema(BaseSchema):
    uuid = fields.String(required=True)


class CallPickupInterceptorUsersSchema(BaseSchema):
    users = fields.Nested(CallPickupInterceptorUserSchema, many=True, required=True)


class CallPickupTargetUserSchema(BaseSchema):
    uuid = fields.String(required=True)


class CallPickupTargetUsersSchema(BaseSchema):
    users = fields.Nested(CallPickupTargetUserSchema, many=True, required=True)
