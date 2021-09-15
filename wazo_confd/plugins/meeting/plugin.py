# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import (
    GuestMeetingItem,
    MeetingList,
    MeetingItem,
    UserMeetingItem,
    UserMeetingList,
)
from wazo_confd.plugins.endpoint_sip.service import build_endpoint_service as build_endpoint_sip_service
from wazo_confd.plugins.tenant.service import build_service as build_tenant_service
from wazo_confd.plugins.user.service import build_service as build_user_service

from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        auth_client = dependencies['auth_client']
        pjsip_doc = dependencies['pjsip_doc']

        hostname = config['beta_meeting_public_hostname']
        port = config['beta_meeting_public_port']

        service = build_service(hostname, port)
        endpoint_sip_service = build_endpoint_sip_service(None, pjsip_doc)
        user_service = build_user_service(provd_client=None)
        tenant_service = build_tenant_service()
        args = [service, user_service, hostname, port]

        api.add_resource(
            MeetingList,
            '/meetings',
            resource_class_args=[
                service,
                user_service,
                tenant_service,
                endpoint_sip_service,
                hostname,
                port,
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
                hostname,
                port,
                auth_client,
            ],
        )
