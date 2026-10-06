# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao

from wazo_confd.helpers.types import PluginDependencies

from .resource import (
    UserCallerIDDefault,
    UserCallerIDList,
    UserMeCallerIDDefault,
    UserMeCallerIDList,
)
from .service import build_service, build_service_default


class Plugin:
    def load(self, dependencies: PluginDependencies):
        api = dependencies['api']

        service = build_service()
        service_default = build_service_default()

        api.add_resource(
            UserMeCallerIDList,
            '/users/me/callerids/outgoing',
            resource_class_args=(service, user_dao),
            endpoint='user_me_callerids_outgoing',
        )
        api.add_resource(
            UserMeCallerIDDefault,
            '/users/me/callerids/outgoing/default',
            resource_class_args=(service_default, user_dao),
            endpoint='user_me_callerids_outgoing_default',
        )

        # admin-oriented APIs
        api.add_resource(
            UserCallerIDList,
            '/users/<uuid:user_id>/callerids/outgoing',
            '/users/<int:user_id>/callerids/outgoing',
            resource_class_args=(service, user_dao),
        )
        api.add_resource(
            UserCallerIDDefault,
            '/users/<uuid:user_id>/callerids/outgoing/default',
            '/users/<int:user_id>/callerids/outgoing/default',
            resource_class_args=(service_default, user_dao),
            endpoint='user_callerids_outgoing_default',
        )
