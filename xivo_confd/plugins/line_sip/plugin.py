# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from wazo_provd_client import Client as ProvdClient

from .resource import LineSipItem, LineSipList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        service = build_service(provd_client)

        api.add_resource(
            LineSipItem,
            '/lines_sip/<int:id>',
            endpoint='lines_sip',
            resource_class_args=(service,)
        )
        api.add_resource(
            LineSipList,
            '/lines_sip',
            resource_class_args=(service,)
        )
