# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import IAXItem, IAXList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']

        service = build_service()

        api.add_resource(
            IAXItem,
            '/endpoints/iax/<int:id>',
            endpoint='endpoint_iax',
            resource_class_args=(service,)
        )
        api.add_resource(
            IAXList,
            '/endpoints/iax',
            resource_class_args=(service,)
        )
