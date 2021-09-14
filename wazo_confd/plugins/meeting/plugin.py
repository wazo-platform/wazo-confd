# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import (
    GuestMeetingItem,
    MeetingList,
    MeetingItem,
    UserMeetingItem,
    UserMeetingList,
)
from wazo_confd.plugins.user.service import build_service as build_user_service

from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        auth_client = dependencies['auth_client']

        hostname = config['beta_meeting_public_hostname']
        port = config['beta_meeting_public_port']

        service = build_service(hostname, port)
        user_service = build_user_service(provd_client=None)
        args = [service, user_service, hostname, port]

        api.add_resource(
            MeetingList,
            '/meetings',
            resource_class_args=args,
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
            resource_class_args=args,
        )
