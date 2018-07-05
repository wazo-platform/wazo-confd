# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class IncallExtensionItem(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, service, incall_dao, extension_dao):
        super(IncallExtensionItem, self).__init__()
        self.service = service
        self.incall_dao = incall_dao
        self.extension_dao = extension_dao

    @required_acl('confd.incalls.{incall_id}.extensions.{extension_id}.delete')
    def delete(self, incall_id, extension_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        incall = self.incall_dao.get(incall_id, tenant_uuids=tenant_uuids)
        extension = self.extension_dao.get(extension_id, tenant_uuids=tenant_uuids)

        self.service.dissociate(incall, extension)
        return '', 204

    @required_acl('confd.incalls.{incall_id}.extensions.{extension_id}.update')
    def put(self, incall_id, extension_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        incall = self.incall_dao.get(incall_id, tenant_uuids=tenant_uuids)
        extension = self.extension_dao.get(extension_id, tenant_uuids=tenant_uuids)

        self.service.associate(incall, extension)
        return '', 204
