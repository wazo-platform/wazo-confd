# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import LineItem, LineList
from .service import build_service


class Plugin(object):

    def load(self, core):
        api = core.api
        provd_client = core.provd_client()

        service = build_service(provd_client)

        api.add_resource(
            LineItem,
            '/lines/<int:id>',
            endpoint='lines',
            resource_class_args=(service,)
        )
        api.add_resource(
            LineList,
            '/lines',
            resource_class_args=(service,)
        )
