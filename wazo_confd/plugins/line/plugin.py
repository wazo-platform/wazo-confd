# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao.resources.pjsip_transport import dao as transport_dao

from wazo_confd.plugins.endpoint_sip.service import (
    build_endpoint_service as build_endpoint_sip_service,
)
from wazo_confd.plugins.line_endpoint.service import build_service_sip

from .resource import LineItem, LineList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']
        pjsip_doc = dependencies['pjsip_doc']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        service = build_service(provd_client)
        endpoint_sip_service = build_endpoint_sip_service(provd_client, pjsip_doc)
        line_endpoint_sip_association_service = build_service_sip(provd_client)

        api.add_resource(
            LineItem,
            '/lines/<int:id>',
            endpoint='lines',
            resource_class_args=(service,),
        )
        api.add_resource(
            LineList,
            '/lines',
            resource_class_args=(
                service,
                endpoint_sip_service,
                line_endpoint_sip_association_service,
                line_dao,
                sip_dao,
                transport_dao,
            ),
        )
