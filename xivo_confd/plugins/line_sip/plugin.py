# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api

from .resource import LineSipItem, LineSipList
from .service import build_service


class Plugin(object):

    def load(self, core):
        provd_client = core.provd_client()

        service = build_service(provd_client)

        api.add_resource(
            LineSipItem,
            '/lines_sip/<int:id>',
            endpoint='lines_sip',
            resource_class_args=(service,)
        )
        api.add_resource(
            LineSipList,
            '/lines_sip',
            resource_class_args=(service,)
        )
