# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd import sysconfd

from .resource import ConfigHistoryDiffResource, ConfigHistoryResource
from .service import ConfigHistoryService


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = ConfigHistoryService(sysconfd)

        api.add_resource(
            ConfigHistoryResource, '/config_history', resource_class_args=(service,)
        )
        api.add_resource(
            ConfigHistoryDiffResource,
            '/config_history/diff',
            resource_class_args=(service,),
        )
