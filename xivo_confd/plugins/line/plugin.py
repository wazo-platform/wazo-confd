# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.line.service import build_service
from xivo_confd.plugins.line.resource import LineItem, LineList


class Plugin(object):

    def load(self, core):
        provd_client = core.provd_client()

        service = build_service(provd_client)

        api.add_resource(LineItem,
                         '/lines/<int:id>',
                         endpoint='lines',
                         resource_class_args=(service,)
                         )
        api.add_resource(LineList,
                         '/lines',
                         resource_class_args=(service,)
                         )
