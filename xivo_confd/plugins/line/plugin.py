# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from wazo_provd_client import Client as ProvdClient

from .resource import LineItem, LineList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        provd_client = ProvdClient(**config['provd'])

        service = build_service(provd_client)

        api.add_resource(
            LineItem,
            '/lines/<int:id>',
            endpoint='lines',
            resource_class_args=(service,)
        )
        api.add_resource(
            LineList,
            '/lines',
            resource_class_args=(service,)
        )
