# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.schedule import dao as schedule_dao

from xivo_confd import api
from .resource import UserScheduleItem
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(UserScheduleItem,
                         '/users/<int:user_id>/schedules/<int:schedule_id>',
                         '/users/<uuid:user_id>/schedules/<int:schedule_id>',
                         endpoint='user_schedules',
                         resource_class_args=(service, user_dao, schedule_dao)
                         )
