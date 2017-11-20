# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class IncallExtensionItem(ConfdResource):

    def __init__(self, service, incall_dao, extension_dao):
        super(IncallExtensionItem, self).__init__()
        self.service = service
        self.incall_dao = incall_dao
        self.extension_dao = extension_dao

    @required_acl('confd.incalls.{incall_id}.extensions.{extension_id}.delete')
    def delete(self, incall_id, extension_id):
        incall = self.incall_dao.get(incall_id)
        extension = self.extension_dao.get(extension_id)
        self.service.dissociate(incall, extension)
        return '', 204

    @required_acl('confd.incalls.{incall_id}.extensions.{extension_id}.update')
    def put(self, incall_id, extension_id):
        incall = self.incall_dao.get(incall_id)
        extension = self.extension_dao.get(extension_id)
        self.service.associate(incall, extension)
        return '', 204
