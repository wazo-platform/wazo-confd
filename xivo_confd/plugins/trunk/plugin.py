# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import TrunkItem, TrunkList
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            TrunkList,
            '/trunks',
            resource_class_args=(service,)
        )

        api.add_resource(
            TrunkItem,
            '/trunks/<int:id>',
            endpoint='trunks',
            resource_class_args=(service,)
        )
