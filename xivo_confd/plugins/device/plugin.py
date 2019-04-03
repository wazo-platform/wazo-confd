# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from .builder import build_dao, build_service
from .resource import (
    DeviceItem,
    DeviceList,
    DeviceAutoprov,
    DeviceSynchronize
)


class Plugin(object):
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        dao = build_dao(provd_client)
        service = build_service(dao, provd_client)

        api.add_resource(
            DeviceItem,
            '/devices/<id>',
            endpoint='devices',
            resource_class_args=(service,)
        )

        api.add_resource(
            DeviceList,
            '/devices',
            resource_class_args=(service,)
        )

        api.add_resource(
            DeviceAutoprov,
            '/devices/<id>/autoprov',
            resource_class_args=(service,)
        )

        api.add_resource(
            DeviceSynchronize,
            '/devices/<id>/synchronize',
            resource_class_args=(service,)
        )
