# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from .service import build_service
from .resource import IncallItem, IncallList


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(IncallList,
                         '/incalls',
                         resource_class_args=(service,)
                         )

        api.add_resource(IncallItem,
                         '/incalls/<int:id>',
                         endpoint='incalls',
                         resource_class_args=(service,)
                         )
