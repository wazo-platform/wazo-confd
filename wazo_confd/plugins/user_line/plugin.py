# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.user import dao as user_dao

from .middleware import UserLineAssociationMiddleWare
from .resource import UserLineItem, UserLineList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        middleware_handle = dependencies['middleware_handle']
        service = build_service()

        user_line_association_middleware = UserLineAssociationMiddleWare(service)
        middleware_handle.register(
            'user_line_association', user_line_association_middleware
        )

        api.add_resource(
            UserLineItem,
            '/users/<int:user_id>/lines/<int:line_id>',
            '/users/<uuid:user_id>/lines/<int:line_id>',
            endpoint='user_lines',
            resource_class_args=(
                service,
                user_dao,
                line_dao,
                user_line_association_middleware,
            ),
        )
        api.add_resource(
            UserLineList,
            '/users/<int:user_id>/lines',
            '/users/<uuid:user_id>/lines',
            resource_class_args=(service, user_dao, line_dao),
        )
