# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.outcall import dao as outcall_dao
from xivo_dao.resources.schedule import dao as schedule_dao

from .resource import OutcallScheduleItem
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            OutcallScheduleItem,
            '/outcalls/<int:outcall_id>/schedules/<int:schedule_id>',
            endpoint='outcall_schedules',
            resource_class_args=(service, outcall_dao, schedule_dao)
        )
