# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class GroupExtensionItem(ConfdResource):

    def __init__(self, service, group_dao, extension_dao):
        super(GroupExtensionItem, self).__init__()
        self.service = service
        self.group_dao = group_dao
        self.extension_dao = extension_dao

    @required_acl('confd.groups.{group_id}.extensions.{extension_id}.delete')
    def delete(self, group_id, extension_id):
        group = self.group_dao.get(group_id)
        extension = self.extension_dao.get(extension_id)
        self.service.dissociate(group, extension)
        return '', 204

    @required_acl('confd.groups.{group_id}.extensions.{extension_id}.update')
    def put(self, group_id, extension_id):
        group = self.group_dao.get(group_id)
        extension = self.extension_dao.get(extension_id)
        self.service.associate(group, extension)
        return '', 204
