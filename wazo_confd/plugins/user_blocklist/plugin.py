# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.types import PluginDependencies
from .resource import (
    UserBlocklistNumberItem,
    UserBlocklistNumberList,
)
from .service import build_service


class UserBlocklistPluginDependencies(PluginDependencies):
    pass


class Plugin:
    def load(self, dependencies: UserBlocklistPluginDependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            UserBlocklistNumberList,
            '/users/me/blocklist/numbers',
            resource_class_args=(service,),
        )
        api.add_resource(
            UserBlocklistNumberItem,
            '/users/me/blocklist/numbers/<uuid:uuid>',
            resource_class_args=(service,),
            endpoint='user_blocklist_numbers',
        )
