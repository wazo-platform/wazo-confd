# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.entity.service import build_service
from xivo_confd.plugins.entity.resource import EntityItem, EntityList


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(EntityList,
                         '/entities',
                         resource_class_args=(service,)
                         )

        api.add_resource(EntityItem,
                         '/entities/<int:id>',
                         endpoint='entities',
                         resource_class_args=(service,)
                         )
