# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao

from .resource import UserFallbackList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            UserFallbackList,
            '/users/<uuid:user_id>/fallbacks',
            '/users/<int:user_id>/fallbacks',
            resource_class_args=(service, user_dao),
        )
