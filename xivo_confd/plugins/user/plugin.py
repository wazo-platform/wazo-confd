# -*- coding: UTF-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_provd_client import new_provisioning_client_from_config

from .resource import UserItem, UserList
from .resource_sub import (
    UserForwardBusy,
    UserForwardList,
    UserForwardNoAnswer,
    UserForwardUnconditional,
    UserServiceDND,
    UserServiceIncallFilter,
    UserServiceList,
)
from .service import (
    build_service,
    build_service_callservice,
    build_service_forward,
)


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        provd_client = new_provisioning_client_from_config(config['provd'])

        service = build_service(provd_client)
        service_callservice = build_service_callservice()
        service_forward = build_service_forward()

        api.add_resource(
            UserItem,
            '/users/<uuid:id>',
            '/users/<int:id>',
            endpoint='users',
            resource_class_args=(service,)
        )

        api.add_resource(
            UserList,
            '/users',
            endpoint='users_list',
            resource_class_args=(service,)
        )

        api.add_resource(
            UserServiceDND,
            '/users/<uuid:user_id>/services/dnd',
            '/users/<int:user_id>/services/dnd',
            resource_class_args=(service_callservice,)
        )

        api.add_resource(
            UserServiceIncallFilter,
            '/users/<uuid:user_id>/services/incallfilter',
            '/users/<int:user_id>/services/incallfilter',
            resource_class_args=(service_callservice,)
        )

        api.add_resource(
            UserServiceList,
            '/users/<uuid:user_id>/services',
            '/users/<int:user_id>/services',
            resource_class_args=(service_callservice,)
        )

        api.add_resource(
            UserForwardBusy,
            '/users/<uuid:user_id>/forwards/busy',
            '/users/<int:user_id>/forwards/busy',
            resource_class_args=(service_forward,)
        )

        api.add_resource(
            UserForwardNoAnswer,
            '/users/<uuid:user_id>/forwards/noanswer',
            '/users/<int:user_id>/forwards/noanswer',
            resource_class_args=(service_forward,)
        )

        api.add_resource(
            UserForwardUnconditional,
            '/users/<uuid:user_id>/forwards/unconditional',
            '/users/<int:user_id>/forwards/unconditional',
            resource_class_args=(service_forward,)
        )

        api.add_resource(
            UserForwardList,
            '/users/<uuid:user_id>/forwards',
            '/users/<int:user_id>/forwards',
            resource_class_args=(service_forward,)
        )
