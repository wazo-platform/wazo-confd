# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.plugins.endpoint_custom.service import build_service
from xivo_confd.plugins.endpoint_custom.resource import CustomItem, CustomList


class Plugin(object):

    def load(self, core):
        api = core.api

        service = build_service()

        api.add_resource(CustomItem,
                         '/endpoints/custom/<int:id>',
                         endpoint='endpoint_custom',
                         resource_class_args=(service,)
                         )
        api.add_resource(CustomList,
                         '/endpoints/custom',
                         resource_class_args=(service,)
                         )
