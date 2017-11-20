# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.line_device.resource import LineDeviceAssociation
from xivo_confd.plugins.line_device.resource import LineDeviceGet
from xivo_confd.plugins.line_device.resource import DeviceLineGet

from xivo_confd.plugins.line_device.service import build_service
from xivo_confd.plugins.device.builder import build_dao as build_device_dao

from xivo_dao.resources.line import dao as line_dao


class Plugin(object):

    def load(self, core):
        provd_client = core.provd_client()
        device_dao = build_device_dao(provd_client)
        service = build_service(provd_client)

        api.add_resource(LineDeviceAssociation,
                         '/lines/<int:line_id>/devices/<device_id>',
                         endpoint='line_devices',
                         resource_class_args=(line_dao, device_dao, service)
                         )

        api.add_resource(LineDeviceGet,
                         '/lines/<int:line_id>/devices',
                         resource_class_args=(line_dao, device_dao, service)
                         )

        api.add_resource(DeviceLineGet,
                         '/devices/<device_id>/lines',
                         resource_class_args=(line_dao, device_dao, service)
                         )
