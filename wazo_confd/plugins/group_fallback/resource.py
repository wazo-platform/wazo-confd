# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource

from .schema import GroupFallbackSchema


class GroupFallbackList(ConfdResource):
    has_tenant_uuid = True
    schema = GroupFallbackSchema

    def __init__(self, service, group_dao):
        super().__init__()
        self.service = service
        self.group_dao = group_dao

    @required_acl('confd.groups.{group_uuid}.fallbacks.read')
    def get(self, group_uuid):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        group = self.group_dao.get(group_uuid, tenant_uuids=tenant_uuids)
        return self.schema().dump(group.fallbacks)

    @required_acl('confd.groups.{group_uuid}.fallbacks.update')
    def put(self, group_uuid):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        group = self.group_dao.get(group_uuid, tenant_uuids=tenant_uuids)
        fallbacks = self.schema().load(request.get_json(force=True))
        self.service.edit(group, fallbacks)
        return '', 204
