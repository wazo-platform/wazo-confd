# Copyright 2017-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class UserScheduleItem(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, service, user_dao, schedule_dao):
        super().__init__()
        self.service = service
        self.user_dao = user_dao
        self.schedule_dao = schedule_dao

    @required_acl('confd.users.{user_id}.schedules.{schedule_id}.delete')
    def delete(self, user_id, schedule_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user = self.user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)
        schedule = self.schedule_dao.get(schedule_id, tenant_uuids=tenant_uuids)
        self.service.dissociate(user, schedule)
        return '', 204

    @required_acl('confd.users.{user_id}.schedules.{schedule_id}.update')
    def put(self, user_id, schedule_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user = self.user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)
        schedule = self.schedule_dao.get(schedule_id, tenant_uuids=tenant_uuids)
        self.service.associate(user, schedule)
        return '', 204
