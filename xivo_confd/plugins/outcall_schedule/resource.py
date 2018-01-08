# -*- coding: UTF-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class OutcallScheduleItem(ConfdResource):

    def __init__(self, service, outcall_dao, schedule_dao):
        super(OutcallScheduleItem, self).__init__()
        self.service = service
        self.outcall_dao = outcall_dao
        self.schedule_dao = schedule_dao

    @required_acl('confd.outcalls.{outcall_id}.schedules.{schedule_id}.delete')
    def delete(self, outcall_id, schedule_id):
        outcall = self.outcall_dao.get(outcall_id)
        schedule = self.schedule_dao.get(schedule_id)
        self.service.dissociate(outcall, schedule)
        return '', 204

    @required_acl('confd.outcalls.{outcall_id}.schedules.{schedule_id}.update')
    def put(self, outcall_id, schedule_id):
        outcall = self.outcall_dao.get(outcall_id)
        schedule = self.schedule_dao.get(schedule_id)
        self.service.associate(outcall, schedule)
        return '', 204
