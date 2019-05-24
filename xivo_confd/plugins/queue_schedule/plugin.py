# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.queue import dao as queue_dao
from xivo_dao.resources.schedule import dao as schedule_dao

from .resource import QueueScheduleItem
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service(queue_dao)

        api.add_resource(
            QueueScheduleItem,
            '/queues/<int:queue_id>/schedules/<int:schedule_id>',
            endpoint='queue_schedules',
            resource_class_args=(service, queue_dao, schedule_dao)
        )
