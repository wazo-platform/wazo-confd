# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource, ListResource, MeResourceMixin

from .schema import UserCallerIDDefaultSchema, UserCallerIDSchema


class UserCallerIDList(ListResource):
    schema = UserCallerIDSchema
    has_tenant_uuid = True

    def __init__(self, service, user_dao):
        self.service = service
        self.user_dao = user_dao

    @required_acl('confd.users.{user_id}.callerids.outgoing.read')
    def get(self, user_id):
        params: dict[str, str] = {}  # NOTE(fblackburn): search is not implemented
        user = self._get_user(user_id)
        total, items = self.service.search(user.id, user.tenant_uuid, params)
        return {'total': total, 'items': self.schema().dump(items, many=True)}

    def post(self):
        return '', 405

    def _get_user(self, user_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        return self.user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)


class UserMeCallerIDList(MeResourceMixin, UserCallerIDList):
    @required_acl('confd.users.me.callerids.outgoing.read')
    def get(self):
        return super().get(self._find_user_uuid())


class UserCallerIDDefault(ConfdResource):
    schema = UserCallerIDDefaultSchema
    has_tenant_uuid = True

    def __init__(self, service, user_dao):
        super().__init__()
        self.service = service
        self.user_dao = user_dao

    @required_acl('confd.users.{user_id}.callerids.outgoing.default.read')
    def get(self, user_id):
        user = self._get_user(user_id)
        return self.schema().dump(self.service.get(user))

    @required_acl('confd.users.{user_id}.callerids.outgoing.default.update')
    def put(self, user_id):
        user = self._get_user(user_id)
        form = self.schema().load(request.get_json(force=True))
        self.service.edit(user, form)
        return '', 204

    def _get_user(self, user_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        return self.user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)


class UserMeCallerIDDefault(MeResourceMixin, UserCallerIDDefault):
    @required_acl('confd.users.me.callerids.outgoing.default.read')
    def get(self):
        return super().get(self._find_user_uuid())

    @required_acl('confd.users.me.callerids.outgoing.default.update')
    def put(self):
        return super().put(self._find_user_uuid())
