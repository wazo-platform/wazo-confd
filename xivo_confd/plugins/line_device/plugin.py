# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.line import dao as line_dao
from xivo_provd_client import new_provisioning_client_from_config

from xivo_confd.plugins.device.builder import build_dao as build_device_dao

from .resource import (
    LineDeviceAssociation,
    LineDeviceGet,
    DeviceLineGet,
)
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        provd_client = new_provisioning_client_from_config(config['provd'])
        device_dao = build_device_dao(provd_client)
        service = build_service(provd_client)

        api.add_resource(
            LineDeviceAssociation,
            '/lines/<int:line_id>/devices/<device_id>',
            endpoint='line_devices',
            resource_class_args=(line_dao, device_dao, service)
        )

        api.add_resource(
            LineDeviceGet,
            '/lines/<int:line_id>/devices',
            resource_class_args=(line_dao, device_dao, service)
        )

        api.add_resource(
            DeviceLineGet,
            '/devices/<device_id>/lines',
            resource_class_args=(line_dao, device_dao, service)
        )
