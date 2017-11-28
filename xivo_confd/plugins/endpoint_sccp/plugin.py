# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .service import build_service
from .resource import SccpItem, SccpList


class Plugin(object):

    def load(self, core):
        api = core.api
        service = build_service()

        api.add_resource(
            SccpItem,
            '/endpoints/sccp/<int:id>',
            endpoint='endpoint_sccp',
            resource_class_args=(service,)
        )
        api.add_resource(
            SccpList,
            '/endpoints/sccp',
            resource_class_args=(service,)
        )
