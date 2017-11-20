# -*- coding: UTF-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.endpoint_sip.service import build_service
from xivo_confd.plugins.endpoint_sip.resource import SipItem, SipList


class Plugin(object):

    def load(self, core):
        provd_client = core.provd_client()

        service = build_service(provd_client)

        api.add_resource(SipItem,
                         '/endpoints/sip/<int:id>',
                         endpoint='endpoint_sip',
                         resource_class_args=(service,)
                         )
        api.add_resource(SipList,
                         '/endpoints/sip',
                         resource_class_args=(service,)
                         )
