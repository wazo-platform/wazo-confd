# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao.resources.pjsip_transport import dao as transport_dao

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
            '/endpoints/sip/<uuid:uuid>',
            endpoint='endpoint_sip',
            resource_class_args=(service, transport_dao),
        )
        api.add_resource(
            SipList,
            '/endpoints/sip',
            resource_class_args=(service, sip_dao, transport_dao)
        )
