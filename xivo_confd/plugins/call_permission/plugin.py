# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api

from .resource import CallPermissionItem, CallPermissionList
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(
            CallPermissionList,
            '/callpermissions',
            resource_class_args=(service,)
        )

        api.add_resource(
            CallPermissionItem,
            '/callpermissions/<int:id>',
            endpoint='callpermissions',
            resource_class_args=(service,)
        )
