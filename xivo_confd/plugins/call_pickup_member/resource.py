# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource

from .schema import (
    CallPickupInterceptorGroupsSchema,
    CallPickupInterceptorUsersSchema,
    CallPickupTargetGroupsSchema,
    CallPickupTargetUsersSchema,
)


class CallPickupInterceptorGroupList(ConfdResource):

    schema = CallPickupInterceptorGroupsSchema
    has_tenant_uuid = True

    def __init__(self, service, call_pickup_dao, group_dao):
        self.service = service
        self.call_pickup_dao = call_pickup_dao
        self.group_dao = group_dao

    @required_acl('confd.callpickups.{call_pickup_id}.interceptors.groups.update')
    def put(self, call_pickup_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        call_pickup = self.call_pickup_dao.get(call_pickup_id, tenant_uuids=tenant_uuids)
        form = self.schema().load(request.get_json()).data
        try:
            interceptors = [self.group_dao.get_by(id=group['id'], tenant_uuids=tenant_uuids)
                            for group in form['groups']]
        except NotFoundError as e:
            raise errors.param_not_found('groups', 'Group', **e.metadata)

        self.service.associate_interceptor_groups(call_pickup, interceptors)
        return '', 204


class CallPickupTargetGroupList(ConfdResource):

    schema = CallPickupTargetGroupsSchema
    has_tenant_uuid = True

    def __init__(self, service, call_pickup_dao, group_dao):
        self.service = service
        self.call_pickup_dao = call_pickup_dao
        self.group_dao = group_dao

    @required_acl('confd.callpickups.{call_pickup_id}.targets.groups.update')
    def put(self, call_pickup_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        call_pickup = self.call_pickup_dao.get(call_pickup_id, tenant_uuids=tenant_uuids)
        form = self.schema().load(request.get_json()).data
        try:
            targets = [self.group_dao.get_by(id=group['id'], tenant_uuids=tenant_uuids)
                       for group in form['groups']]
        except NotFoundError as e:
            raise errors.param_not_found('groups', 'Group', **e.metadata)

        self.service.associate_target_groups(call_pickup, targets)
        return '', 204


class CallPickupInterceptorUserList(ConfdResource):

    schema = CallPickupInterceptorUsersSchema
    has_tenant_uuid = True

    def __init__(self, service, call_pickup_dao, user_dao):
        self.service = service
        self.call_pickup_dao = call_pickup_dao
        self.user_dao = user_dao

    @required_acl('confd.callpickups.{call_pickup_id}.interceptors.users.update')
    def put(self, call_pickup_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        call_pickup = self.call_pickup_dao.get(call_pickup_id, tenant_uuids=tenant_uuids)
        form = self.schema().load(request.get_json()).data
        try:
            interceptors = [self.user_dao.get_by(uuid=user['uuid'], tenant_uuids=tenant_uuids)
                            for user in form['users']]
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_interceptor_users(call_pickup, interceptors)
        return '', 204


class CallPickupTargetUserList(ConfdResource):

    schema = CallPickupTargetUsersSchema

    def __init__(self, service, call_pickup_dao, user_dao):
        self.service = service
        self.call_pickup_dao = call_pickup_dao
        self.user_dao = user_dao

    @required_acl('confd.callpickups.{call_pickup_id}.targets.users.update')
    def put(self, call_pickup_id):
        call_pickup = self.call_pickup_dao.get(call_pickup_id)
        form = self.schema().load(request.get_json()).data
        try:
            targets = [self.user_dao.get_by(uuid=user['uuid']) for user in form['users']]
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_target_users(call_pickup, targets)
        return '', 204
