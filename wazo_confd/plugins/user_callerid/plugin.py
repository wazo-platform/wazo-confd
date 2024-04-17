# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import UserCallerIDList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']

        service = build_service()

        api.add_resource(
            UserCallerIDList,
            '/users/<uuid:user_id>/callerids/outgoing',
            '/users/<int:user_id>/callerids/outgoing',
            resource_class_args=(service,),
        )
