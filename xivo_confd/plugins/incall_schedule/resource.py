# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class IncallScheduleItem(ConfdResource):

    def __init__(self, service, incall_dao, schedule_dao):
        super(IncallScheduleItem, self).__init__()
        self.service = service
        self.incall_dao = incall_dao
        self.schedule_dao = schedule_dao

    @required_acl('confd.incalls.{incall_id}.schedules.{schedule_id}.delete')
    def delete(self, incall_id, schedule_id):
        incall = self.incall_dao.get(incall_id)
        schedule = self.schedule_dao.get(schedule_id)
        self.service.dissociate(incall, schedule)
        return '', 204

    @required_acl('confd.incalls.{incall_id}.schedules.{schedule_id}.update')
    def put(self, incall_id, schedule_id):
        incall = self.incall_dao.get(incall_id)
        schedule = self.schedule_dao.get(schedule_id)
        self.service.associate(incall, schedule)
        return '', 204
