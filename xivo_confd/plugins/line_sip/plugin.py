# -*- coding: UTF-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_provd_client import new_provisioning_client_from_config

from .resource import LineSipItem, LineSipList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        provd_client = new_provisioning_client_from_config(config['provd'])

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
