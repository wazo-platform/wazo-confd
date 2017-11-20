# -*- coding: UTF-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.line_sip.service import build_service
from xivo_confd.plugins.line_sip.resource import LineSipItem, LineSipList


class Plugin(object):

    def load(self, core):
        provd_client = core.provd_client()

        service = build_service(provd_client)

        api.add_resource(LineSipItem,
                         '/lines_sip/<int:id>',
                         endpoint='lines_sip',
                         resource_class_args=(service,)
                         )
        api.add_resource(LineSipList,
                         '/lines_sip',
                         resource_class_args=(service,)
                         )
