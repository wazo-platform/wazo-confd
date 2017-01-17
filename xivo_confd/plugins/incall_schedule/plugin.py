# -*- coding: utf-8 -*-
#
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.schedule import dao as schedule_dao

from xivo_confd import api
from .resource import IncallScheduleItem
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(IncallScheduleItem,
                         '/incalls/<int:incall_id>/schedules/<int:schedule_id>',
                         endpoint='incall_schedules',
                         resource_class_args=(service, incall_dao, schedule_dao)
                         )
