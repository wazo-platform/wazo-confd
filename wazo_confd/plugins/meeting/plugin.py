# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import (
    GuestMeetingItem,
    MeetingList,
    MeetingItem,
    UserMeetingItem,
    UserMeetingList,
)
from wazo_confd import bus, sysconfd
from wazo_confd._bus import InstantBusPublisher
from wazo_confd.plugins.endpoint_sip.service import (
    build_endpoint_service as build_endpoint_sip_service,
)
from wazo_confd.plugins.endpoint_sip.service import (
    build_template_service as build_endpoint_sip_template_service,
)
from wazo_confd.plugins.extension_feature.service import (
    build_service as build_extension_features_service,
)
from wazo_confd.plugins.ingress_http.service import (
    build_service as build_ingress_http_service,
)
from wazo_confd.plugins.tenant.service import build_service as build_tenant_service
from wazo_confd.plugins.user.service import build_service as build_user_service

from .bus_consume import MeetingBusEventHandler
from .notifier import Notifier
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        auth_client = dependencies['auth_client']
        bus_consumer = dependencies['bus_consumer']
        config = dependencies['config']
        pjsip_doc = dependencies['pjsip_doc']

        ingress_http_service = build_ingress_http_service()
        extension_features_service = build_extension_features_service()
        api_notifier = Notifier(
            bus, sysconfd, ingress_http_service, extension_features_service
        )
        service = build_service(api_notifier)

        instant_bus_publisher = InstantBusPublisher.from_config(
            config['bus'],
            config['uuid'],
        )
        bus_notifier = Notifier(
            instant_bus_publisher,
            sysconfd,
            ingress_http_service,
            extension_features_service,
        )
        bus_event_handler = MeetingBusEventHandler(service, bus_notifier)
        bus_event_handler.subscribe(bus_consumer)

        endpoint_sip_service = build_endpoint_sip_service(None, pjsip_doc)
        endpoint_sip_template_service = build_endpoint_sip_template_service(
            None, pjsip_doc
        )
        user_service = build_user_service(provd_client=None)
        tenant_service = build_tenant_service()
        args = [service, user_service, ingress_http_service, extension_features_service]

        api.add_resource(
            MeetingList,
            '/meetings',
            resource_class_args=[
                service,
                user_service,
                tenant_service,
                endpoint_sip_service,
                endpoint_sip_template_service,
                ingress_http_service,
                extension_features_service,
            ],
        )
        api.add_resource(
            MeetingItem,
            '/meetings/<uuid:uuid>',
            endpoint='meetings',
            resource_class_args=args,
        )
        api.add_resource(
            GuestMeetingItem,
            '/guests/me/meetings/<uuid:uuid>',
            resource_class_args=args,
        )

        args.append(auth_client)
        api.add_resource(
            UserMeetingItem,
            '/users/me/meetings/<uuid:uuid>',
            resource_class_args=args,
        )
        api.add_resource(
            UserMeetingList,
            '/users/me/meetings',
            resource_class_args=[
                service,
                user_service,
                tenant_service,
                endpoint_sip_service,
                endpoint_sip_template_service,
                ingress_http_service,
                extension_features_service,
                auth_client,
            ],
        )
