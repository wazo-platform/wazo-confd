# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.call_log.service import build_service
from xivo_confd.plugins.call_log.resource import CallLog
from xivo_confd.plugins.call_log import serializer
from xivo_confd.plugins.call_log import mapper


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(CallLog,
                         '/call_logs',
                         resource_class_args=(service, serializer, mapper)
                         )
