# -*- coding: utf-8 -*-

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

from flask import url_for

from xivo_dao.alchemy.schedule import Schedule

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import ScheduleSchema


class ScheduleList(ListResource):

    model = Schedule
    schema = ScheduleSchema

    def build_headers(self, schedule):
        return {'Location': url_for('schedules', id=schedule.id, _external=True)}

    @required_acl('confd.schedules.create')
    def post(self):
        return super(ScheduleList, self).post()

    @required_acl('confd.schedules.read')
    def get(self):
        return super(ScheduleList, self).get()


class ScheduleItem(ItemResource):

    schema = ScheduleSchema

    @required_acl('confd.schedules.{id}.read')
    def get(self, id):
        return super(ScheduleItem, self).get(id)

    @required_acl('confd.schedules.{id}.update')
    def put(self, id):
        return super(ScheduleItem, self).put(id)

    @required_acl('confd.schedules.{id}.delete')
    def delete(self, id):
        return super(ScheduleItem, self).delete(id)
