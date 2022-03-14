# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd import bus
from xivo_dao.resources.meeting import dao as meeting_dao
from xivo_dao.resources.meeting_authorization import dao as meeting_authorization_dao

from .resource import (
    GuestMeetingAuthorizationList,
    GuestMeetingAuthorizationItem,
    UserMeetingAuthorizationList,
    UserMeetingAuthorizationAccept,
    UserMeetingAuthorizationReject,
)
from .notifier import Notifier
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        api_notifier = Notifier(bus)
        service = build_service(api_notifier)

        api.add_resource(
            GuestMeetingAuthorizationList,
            '/guests/<guest_uuid>/meetings/<uuid:meeting_uuid>/authorizations',
            endpoint='guest_meeting_authorization_list',
            resource_class_args=[service, meeting_dao],
        )

        api.add_resource(
            GuestMeetingAuthorizationItem,
            '/guests/<guest_uuid>/meetings/<uuid:meeting_uuid>/authorizations/<uuid:authorization_uuid>',
            endpoint='guest_meeting_authorization',
            resource_class_args=[service, meeting_dao],
        )

        api.add_resource(
            UserMeetingAuthorizationList,
            '/users/me/meetings/<uuid:meeting_uuid>/authorizations',
            endpoint='user_meeting_authorization_list',
            resource_class_args=[service, meeting_dao],
        )

        api.add_resource(
            UserMeetingAuthorizationAccept,
            '/users/me/meetings/<uuid:meeting_uuid>/authorizations/<uuid:authorization_uuid>/accept',
            endpoint='user_meeting_authorization_accept',
            resource_class_args=[service, meeting_authorization_dao],
        )

        api.add_resource(
            UserMeetingAuthorizationReject,
            '/users/me/meetings/<uuid:meeting_uuid>/authorizations/<uuid:authorization_uuid>/reject',
            endpoint='user_meeting_authorization_reject',
            resource_class_args=[service, meeting_authorization_dao],
        )
