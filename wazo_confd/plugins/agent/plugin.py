# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import AgentItem, AgentList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(AgentList, '/agents', resource_class_args=(service,))

        api.add_resource(
            AgentItem,
            '/agents/<int:id>',
            endpoint='agents',
            resource_class_args=(service,),
        )
