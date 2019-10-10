# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.line import dao as line_dao
from wazo_provd_client import Client as ProvdClient

from wazo_confd.plugins.device.builder import (
    build_dao as build_device_dao,
    build_device_updater,
)

from .resource import LineDeviceAssociation, LineDeviceGet, DeviceLineGet
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        device_dao = build_device_dao(provd_client)
        device_updater = build_device_updater(provd_client)
        service = build_service(provd_client, device_updater)

        api.add_resource(
            LineDeviceAssociation,
            '/lines/<int:line_id>/devices/<device_id>',
            endpoint='line_devices',
            resource_class_args=(line_dao, device_dao, service),
        )

        api.add_resource(
            LineDeviceGet,
            '/lines/<int:line_id>/devices',
            resource_class_args=(line_dao, device_dao, service),
        )

        api.add_resource(
            DeviceLineGet,
            '/devices/<device_id>/lines',
            resource_class_args=(line_dao, device_dao, service),
        )
