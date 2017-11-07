# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from .service import build_service
from .resource import ContextItem, ContextList


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(ContextList,
                         '/contexts',
                         resource_class_args=(service,))

        api.add_resource(ContextItem,
                         '/contexts/<int:id>',
                         endpoint='contexts',
                         resource_class_args=(service,))
