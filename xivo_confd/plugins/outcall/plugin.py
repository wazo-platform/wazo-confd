# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from .service import build_service
from .resource import OutcallItem, OutcallList


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(OutcallList,
                         '/outcalls',
                         resource_class_args=(service,)
                         )

        api.add_resource(OutcallItem,
                         '/outcalls/<int:id>',
                         endpoint='outcalls',
                         resource_class_args=(service,)
                         )
