# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class OutcallCallPermissionAssociation(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, service, outcall_dao, call_permission_dao):
        super(OutcallCallPermissionAssociation, self).__init__()
        self.service = service
        self.outcall_dao = outcall_dao
        self.call_permission_dao = call_permission_dao

    @required_acl(
        'confd.outcalls.{outcall_id}.callpermissions.{call_permission_id}.update'
    )
    def put(self, outcall_id, call_permission_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        outcall = self.outcall_dao.get(outcall_id, tenant_uuids=tenant_uuids)
        call_permission = self.call_permission_dao.get(
            call_permission_id, tenant_uuids=tenant_uuids
        )
        self.service.associate(outcall, call_permission)
        return '', 204

    @required_acl(
        'confd.outcalls.{outcall_id}.callpermissions.{call_permission_id}.delete'
    )
    def delete(self, outcall_id, call_permission_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        outcall = self.outcall_dao.get(outcall_id, tenant_uuids=tenant_uuids)
        call_permission = self.call_permission_dao.get(
            call_permission_id, tenant_uuids=tenant_uuids
        )
        self.service.dissociate(outcall, call_permission)
        return '', 204
