# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api

from .resource import ScheduleItem, ScheduleList
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(
            ScheduleList,
            '/schedules',
            resource_class_args=(service,)
        )

        api.add_resource(
            ScheduleItem,
            '/schedules/<int:id>',
            endpoint='schedules',
            resource_class_args=(service,)
        )
