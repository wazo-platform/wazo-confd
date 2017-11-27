# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.schedule import dao as schedule_dao

from xivo_confd import api

from .resource import IncallScheduleItem
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(
            IncallScheduleItem,
            '/incalls/<int:incall_id>/schedules/<int:schedule_id>',
            endpoint='incall_schedules',
            resource_class_args=(service, incall_dao, schedule_dao)
        )
