# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .middleware import SwitchboardMemberMiddleWare
from .resource import SwitchboardMemberUserItem
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        middleware_handle = dependencies['middleware_handle']
        service = build_service()
        switchboard_member_middleware = SwitchboardMemberMiddleWare(service)
        middleware_handle.register('switchboard_member', switchboard_member_middleware)

        api.add_resource(
            SwitchboardMemberUserItem,
            '/switchboards/<uuid:switchboard_uuid>/members/users',
            endpoint='switchboard_member_users',
            resource_class_args=(switchboard_member_middleware,),
        )
