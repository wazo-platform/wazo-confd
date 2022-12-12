# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from .middleware import LineMiddleWare

from xivo_dao.resources.endpoint_custom import dao as endpoint_custom_dao
from xivo_dao.resources.endpoint_sccp import dao as endpoint_sccp_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao.resources.pjsip_transport import dao as transport_dao

from wazo_confd.plugins.extension.service import (
    build_service as build_extension_service,
)
from wazo_confd.plugins.line_extension.service import (
    build_service as build_extension_line_service,
)
from wazo_confd.plugins.endpoint_sip.service import (
    build_endpoint_service as build_endpoint_sip_service,
)
from wazo_confd.plugins.line_endpoint.service import build_service_custom
from wazo_confd.plugins.line_endpoint.service import build_service_sip
from wazo_confd.plugins.line_endpoint.service import build_service_sccp
from wazo_confd.plugins.endpoint_sccp.service import (
    build_service as build_endpoint_sccp_service,
)
from wazo_confd.plugins.endpoint_custom.service import (
    build_service as build_endpoint_custom_service,
)

from .resource import LineItem, LineList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']
        middleware_handle = dependencies['middleware_handle']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        service = build_service(provd_client)

        line_middleware = LineMiddleWare(service, middleware_handle)
        middleware_handle.register('line', line_middleware)

        api.add_resource(
            LineItem,
            '/lines/<int:id>',
            endpoint='lines',
            resource_class_args=(service, line_middleware),
        )
        api.add_resource(
            LineList,
            '/lines',
            resource_class_args=(service, line_middleware),
        )
