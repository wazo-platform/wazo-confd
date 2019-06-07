# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from .resource import SipItem, SipList
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

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
