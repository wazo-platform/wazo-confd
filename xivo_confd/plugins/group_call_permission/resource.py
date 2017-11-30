# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class GroupCallPermissionAssociation(ConfdResource):

    def __init__(self, service, group_dao, call_permission_dao):
        super(GroupCallPermissionAssociation, self).__init__()
        self.service = service
        self.group_dao = group_dao
        self.call_permission_dao = call_permission_dao

    @required_acl('confd.groups.{group_id}.callpermissions.{call_permission_id}.update')
    def put(self, group_id, call_permission_id):
        group = self.group_dao.get(group_id)
        call_permission = self.call_permission_dao.get(call_permission_id)
        self.service.associate(group, call_permission)
        return '', 204

    @required_acl('confd.groups.{group_id}.callpermissions.{call_permission_id}.delete')
    def delete(self, group_id, call_permission_id):
        group = self.group_dao.get(group_id)
        call_permission = self.call_permission_dao.get(call_permission_id)
        self.service.dissociate(group, call_permission)
        return '', 204
