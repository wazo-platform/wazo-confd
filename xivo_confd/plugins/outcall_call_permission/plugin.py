# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.outcall import dao as outcall_dao
from xivo_dao.resources.call_permission import dao as call_permission_dao

from .resource import OutcallCallPermissionAssociation
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            OutcallCallPermissionAssociation,
            '/outcalls/<int:outcall_id>/callpermissions/<int:call_permission_id>',
            endpoint='outcall_call_permissions',
            resource_class_args=(service, outcall_dao, call_permission_dao)
        )
