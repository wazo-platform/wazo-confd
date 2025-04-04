# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from ..user_import.wazo_user_service import build_service as build_wazo_user_service
from .middleware import UserMiddleWare
from .resource import UserItem, UserList
from .service import build_service, build_service_callservice, build_service_forward
from .sub_resources.middleware import UserForwardMiddleWare
from .sub_resources.resource import (
    UserForwardBusy,
    UserForwardList,
    UserForwardNoAnswer,
    UserForwardUnconditional,
    UserServiceDND,
    UserServiceIncallFilter,
    UserServiceList,
)


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']
        middleware_handle = dependencies['middleware_handle']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        service = build_service(
            provd_client, config['paginated_user_strategy_threshold']
        )
        service_callservice = build_service_callservice()
        service_forward = build_service_forward()
        wazo_user_service = build_wazo_user_service()

        user_middleware = UserMiddleWare(service, wazo_user_service, middleware_handle)
        middleware_handle.register('user', user_middleware)

        user_forward_association_middleware = UserForwardMiddleWare(service_forward)
        middleware_handle.register(
            'user_forward_association', user_forward_association_middleware
        )

        api.add_resource(
            UserItem,
            '/users/<uuid:id>',
            '/users/<int:id>',
            endpoint='users',
            resource_class_args=(
                service,
                user_middleware,
            ),
        )

        api.add_resource(
            UserList,
            '/users',
            endpoint='users_list',
            resource_class_args=(
                service,
                user_middleware,
            ),
        )

        api.add_resource(
            UserServiceDND,
            '/users/<uuid:user_id>/services/dnd',
            '/users/<int:user_id>/services/dnd',
            resource_class_args=(service_callservice,),
        )

        api.add_resource(
            UserServiceIncallFilter,
            '/users/<uuid:user_id>/services/incallfilter',
            '/users/<int:user_id>/services/incallfilter',
            resource_class_args=(service_callservice,),
        )

        api.add_resource(
            UserServiceList,
            '/users/<uuid:user_id>/services',
            '/users/<int:user_id>/services',
            resource_class_args=(service_callservice,),
        )

        api.add_resource(
            UserForwardBusy,
            '/users/<uuid:user_id>/forwards/busy',
            '/users/<int:user_id>/forwards/busy',
            resource_class_args=(service_forward,),
        )

        api.add_resource(
            UserForwardNoAnswer,
            '/users/<uuid:user_id>/forwards/noanswer',
            '/users/<int:user_id>/forwards/noanswer',
            resource_class_args=(service_forward,),
        )

        api.add_resource(
            UserForwardUnconditional,
            '/users/<uuid:user_id>/forwards/unconditional',
            '/users/<int:user_id>/forwards/unconditional',
            resource_class_args=(service_forward,),
        )

        api.add_resource(
            UserForwardList,
            '/users/<uuid:user_id>/forwards',
            '/users/<int:user_id>/forwards',
            resource_class_args=(
                service_forward,
                user_forward_association_middleware,
            ),
        )
