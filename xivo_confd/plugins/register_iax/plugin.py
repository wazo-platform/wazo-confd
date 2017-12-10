# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import RegisterIAXItem, RegisterIAXList
from .service import build_service


class Plugin(object):

    def load(self, core):
        api = core.api
        service = build_service()

        api.add_resource(
            RegisterIAXList,
            '/registers/iax',
            resource_class_args=(service,)
        )

        api.add_resource(
            RegisterIAXItem,
            '/registers/iax/<int:id>',
            endpoint='register_iax',
            resource_class_args=(service,)
        )
