# Copyright 2017-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.schedule import Schedule

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import ScheduleSchema


class ScheduleList(ListResource):

    model = Schedule
    schema = ScheduleSchema

    def build_headers(self, schedule):
        return {'Location': url_for('schedules', id=schedule.id, _external=True)}

    @required_acl('confd.schedules.create')
    def post(self):
        return super().post()

    @required_acl('confd.schedules.read')
    def get(self):
        return super().get()


class ScheduleItem(ItemResource):

    schema = ScheduleSchema
    has_tenant_uuid = True

    @required_acl('confd.schedules.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.schedules.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.schedules.{id}.delete')
    def delete(self, id):
        return super().delete(id)
