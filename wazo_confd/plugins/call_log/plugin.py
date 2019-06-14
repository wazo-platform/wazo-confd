# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import serializer
from . import mapper
from .resource import CallLog
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            CallLog,
            '/call_logs',
            resource_class_args=(service, serializer, mapper)
        )