# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from .resource import (
    LineEndpointAssociationSip,
    LineEndpointAssociationSccp,
    LineEndpointAssociationCustom,
)
from .service import (
    build_service_sip,
    build_service_sccp,
    build_service_custom,
)
from .middleware import (
    LineEndpointCustomMiddleWare,
    LineEndpointSCCPMiddleWare,
    LineEndpointSIPMiddleWare,
)


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']
        middleware_handle = dependencies['middleware_handle']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        service_sip = build_service_sip(provd_client)
        service_sccp = build_service_sccp(provd_client)
        service_custom = build_service_custom(provd_client)

        line_endpoint_custom_middleware = LineEndpointCustomMiddleWare(service_custom)
        line_endpoint_sccp_middleware = LineEndpointSCCPMiddleWare(service_sccp)
        line_endpoint_sip_middleware = LineEndpointSIPMiddleWare(service_sip)
        middleware_handle.register(
            'line_endpoint_custom', line_endpoint_custom_middleware
        )
        middleware_handle.register('line_endpoint_sccp', line_endpoint_sccp_middleware)
        middleware_handle.register('line_endpoint_sip', line_endpoint_sip_middleware)

        api.add_resource(
            LineEndpointAssociationSip,
            '/lines/<int:line_id>/endpoints/sip/<uuid:endpoint_uuid>',
            endpoint='line_endpoint_sip',
            resource_class_args=(line_endpoint_sip_middleware,),
        )
        api.add_resource(
            LineEndpointAssociationSccp,
            '/lines/<int:line_id>/endpoints/sccp/<int:endpoint_id>',
            endpoint='line_endpoint_sccp',
            resource_class_args=(line_endpoint_sccp_middleware,),
        )
        api.add_resource(
            LineEndpointAssociationCustom,
            '/lines/<int:line_id>/endpoints/custom/<int:endpoint_id>',
            endpoint='line_endpoint_custom',
            resource_class_args=(line_endpoint_custom_middleware,),
        )
