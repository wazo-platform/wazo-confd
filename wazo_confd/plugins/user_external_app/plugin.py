# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao

from .resource import UserExternalAppItem, UserExternalAppList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            UserExternalAppList,
            '/users/<uuid:user_uuid>/external/apps',
            '/users/<int:user_uuid>/external/apps',
            resource_class_args=(service, user_dao),
        )

        api.add_resource(
            UserExternalAppItem,
            '/users/<uuid:user_uuid>/external/apps/<name>',
            '/users/<int:user_uuid>/external/apps/<name>',
            endpoint='user_external_apps',
            resource_class_args=(service, user_dao),
        )
