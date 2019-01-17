# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class GroupScheduleItem(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, service, group_dao, schedule_dao):
        super(GroupScheduleItem, self).__init__()
        self.service = service
        self.group_dao = group_dao
        self.schedule_dao = schedule_dao

    @required_acl('confd.groups.{group_id}.schedules.{schedule_id}.delete')
    def delete(self, group_id, schedule_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        group = self.group_dao.get(group_id, tenant_uuids=tenant_uuids)
        schedule = self.schedule_dao.get(schedule_id, tenant_uuids=tenant_uuids)
        self.service.dissociate(group, schedule)
        return '', 204

    @required_acl('confd.groups.{group_id}.schedules.{schedule_id}.update')
    def put(self, group_id, schedule_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        group = self.group_dao.get(group_id, tenant_uuids=tenant_uuids)
        schedule = self.schedule_dao.get(schedule_id, tenant_uuids=tenant_uuids)
        self.service.associate(group, schedule)
        return '', 204
