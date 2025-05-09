# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.types import PluginDependencies

from .resource import (
    BlocklistNumberItem,
    BlocklistNumberList,
    UserBlocklistNumberList,
    UserMeBlocklistNumberItem,
    UserMeBlocklistNumberList,
)
from .service import build_service


class Plugin:
    def load(self, dependencies: PluginDependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            UserMeBlocklistNumberList,
            '/users/me/blocklist/numbers',
            resource_class_args=(service,),
        )
        api.add_resource(
            UserMeBlocklistNumberItem,
            '/users/me/blocklist/numbers/<uuid:uuid>',
            resource_class_args=(service,),
            endpoint='user_me_blocklist_numbers',
        )

        # admin-oriented APIs
        api.add_resource(
            UserBlocklistNumberList,
            '/users/<uuid:user_uuid>/blocklist/numbers',
            resource_class_args=(service,),
        )
        api.add_resource(
            BlocklistNumberList,
            '/users/blocklist/numbers',
            resource_class_args=(service,),
        )
        api.add_resource(
            BlocklistNumberItem,
            '/users/blocklist/numbers/<uuid:uuid>',
            resource_class_args=(service,),
            endpoint='user_blocklist_numbers',
        )
