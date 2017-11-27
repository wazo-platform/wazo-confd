# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api

from .resource import CallLog
from .service import build_service
from . import serializer
from . import mapper


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(
            CallLog,
            '/call_logs',
            resource_class_args=(service, serializer, mapper)
        )
