# -*- coding: UTF-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import EntityItem, EntityList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        tokens = dependencies['tokens']
        service = build_service()

        api.add_resource(
            EntityList,
            '/entities',
            resource_class_args=(service, tokens)
        )

        api.add_resource(
            EntityItem,
            '/entities/<int:id>',
            endpoint='entities',
            resource_class_args=(service,)
        )
