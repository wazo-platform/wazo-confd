# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from .resource import UserListV2, UserItem, UserList
from .resource_sub import (
    UserForwardBusy,
    UserForwardList,
    UserForwardNoAnswer,
    UserForwardUnconditional,
    UserServiceDND,
    UserServiceIncallFilter,
    UserServiceList,
)
from .service import build_service, build_service_callservice, build_service_forward
from ..user_import.wazo_user_service import build_service as build_wazo_user_service


class Plugin:
    def load(self, dependencies):
        api_v1_1 = dependencies['api_v1_1']
        api_v2_0 = dependencies['api_v2_0']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        service = build_service(provd_client)
        wazo_user_service = build_wazo_user_service()
        service_callservice = build_service_callservice()
        service_forward = build_service_forward()

        api_v1_1.add_resource(
            UserItem,
            '/users/<uuid:id>',
            '/users/<int:id>',
            endpoint='users',
            resource_class_args=(service,),
        )

        api_v1_1.add_resource(
            UserList, '/users', endpoint='users_list', resource_class_args=(service,)
        )

        api_v2_0.add_resource(
            UserListV2,
            '/users',
            endpoint='users_list_v2.0',
            resource_class_args=(
                service,
                wazo_user_service,
            ),
        )

        api_v1_1.add_resource(
            UserServiceDND,
            '/users/<uuid:user_id>/services/dnd',
            '/users/<int:user_id>/services/dnd',
            resource_class_args=(service_callservice,),
        )

        api_v1_1.add_resource(
            UserServiceIncallFilter,
            '/users/<uuid:user_id>/services/incallfilter',
            '/users/<int:user_id>/services/incallfilter',
            resource_class_args=(service_callservice,),
        )

        api_v1_1.add_resource(
            UserServiceList,
            '/users/<uuid:user_id>/services',
            '/users/<int:user_id>/services',
            resource_class_args=(service_callservice,),
        )

        api_v1_1.add_resource(
            UserForwardBusy,
            '/users/<uuid:user_id>/forwards/busy',
            '/users/<int:user_id>/forwards/busy',
            resource_class_args=(service_forward,),
        )

        api_v1_1.add_resource(
            UserForwardNoAnswer,
            '/users/<uuid:user_id>/forwards/noanswer',
            '/users/<int:user_id>/forwards/noanswer',
            resource_class_args=(service_forward,),
        )

        api_v1_1.add_resource(
            UserForwardUnconditional,
            '/users/<uuid:user_id>/forwards/unconditional',
            '/users/<int:user_id>/forwards/unconditional',
            resource_class_args=(service_forward,),
        )

        api_v1_1.add_resource(
            UserForwardList,
            '/users/<uuid:user_id>/forwards',
            '/users/<int:user_id>/forwards',
            resource_class_args=(service_forward,),
        )
