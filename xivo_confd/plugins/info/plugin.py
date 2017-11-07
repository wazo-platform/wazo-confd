# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.info.service import build_service
from xivo_confd.plugins.info.resource import Info


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(Info,
                         '/infos',
                         resource_class_args=(service,)
                         )
