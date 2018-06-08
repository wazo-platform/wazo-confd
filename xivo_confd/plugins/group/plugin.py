# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import GroupItem, GroupList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            GroupList,
            '/groups',
            resource_class_args=(service,)
        )

        api.add_resource(
            GroupItem,
            '/groups/<int:id>',
            endpoint='groups',
            resource_class_args=(service,)
        )
