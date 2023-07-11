# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.tenant import dao as tenant_dao

from .resource import CallPermissionItem, CallPermissionList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            CallPermissionList, '/callpermissions', resource_class_args=(tenant_dao, service)
        )

        api.add_resource(
            CallPermissionItem,
            '/callpermissions/<int:id>',
            endpoint='callpermissions',
            resource_class_args=(service,),
        )
