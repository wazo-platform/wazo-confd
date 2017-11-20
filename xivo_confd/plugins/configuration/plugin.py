# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.configuration.service import build_service
from xivo_confd.plugins.configuration.resource import LiveReloadResource


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(LiveReloadResource,
                         '/configuration/live_reload',
                         resource_class_args=(service,)
                         )
