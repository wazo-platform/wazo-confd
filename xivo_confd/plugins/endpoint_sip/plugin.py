# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_provd_client import new_provisioning_client_from_config
from wazo_provd_client import Client as ProvdClient

from .resource import SipItem, SipList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        provd_client = ProvdClient(**config['provd'])

        service = build_service(provd_client)

        api.add_resource(
            SipItem,
            '/endpoints/sip/<int:id>',
            endpoint='endpoint_sip',
            resource_class_args=(service,)
        )
        api.add_resource(
            SipList,
            '/endpoints/sip',
            resource_class_args=(service,)
        )
