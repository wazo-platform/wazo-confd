# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import SIPGeneralList
from .service import build_service


class Plugin(object):

    def load(self, core):
        api = core.api
        service = build_service()

        api.add_resource(
            SIPGeneralList,
            '/asterisk/sip/general',
            resource_class_args=(service,)
        )
