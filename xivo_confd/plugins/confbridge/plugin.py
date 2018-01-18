# -*- coding: UTF-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import ConfBridgeWazoDefaultBridgeList, ConfBridgeWazoDefaultUserList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            ConfBridgeWazoDefaultBridgeList,
            '/asterisk/confbridge/wazo_default_bridge',
            resource_class_args=(service,)
        )

        api.add_resource(
            ConfBridgeWazoDefaultUserList,
            '/asterisk/confbridge/wazo_default_user',
            resource_class_args=(service,)
        )
