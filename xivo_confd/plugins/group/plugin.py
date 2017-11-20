# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from .service import build_service
from .resource import GroupItem, GroupList


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(GroupList,
                         '/groups',
                         resource_class_args=(service,)
                         )

        api.add_resource(GroupItem,
                         '/groups/<int:id>',
                         endpoint='groups',
                         resource_class_args=(service,)
                         )
