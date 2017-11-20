# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.call_permission.service import build_service
from xivo_confd.plugins.call_permission.resource import CallPermissionItem, CallPermissionList


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(CallPermissionList,
                         '/callpermissions',
                         resource_class_args=(service,)
                         )

        api.add_resource(CallPermissionItem,
                         '/callpermissions/<int:id>',
                         endpoint='callpermissions',
                         resource_class_args=(service,)
                         )
