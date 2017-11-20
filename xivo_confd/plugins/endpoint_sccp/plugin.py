# -*- coding: UTF-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.plugins.endpoint_sccp.service import build_service
from xivo_confd.plugins.endpoint_sccp.resource import SccpItem, SccpList


class Plugin(object):

    def load(self, core):
        api = core.api

        service = build_service()

        api.add_resource(SccpItem,
                         '/endpoints/sccp/<int:id>',
                         endpoint='endpoint_sccp',
                         resource_class_args=(service,)
                         )
        api.add_resource(SccpList,
                         '/endpoints/sccp',
                         resource_class_args=(service,)
                         )
