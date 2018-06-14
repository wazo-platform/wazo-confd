# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class QueueExtensionItem(ConfdResource):

    def __init__(self, service, queue_dao, extension_dao):
        super(QueueExtensionItem, self).__init__()
        self.service = service
        self.queue_dao = queue_dao
        self.extension_dao = extension_dao

    @required_acl('confd.queues.{queue_id}.extensions.{extension_id}.delete')
    def delete(self, queue_id, extension_id):
        queue = self.queue_dao.get(queue_id)
        extension = self.extension_dao.get(extension_id)
        self.service.dissociate(queue, extension)
        return '', 204

    @required_acl('confd.queues.{queue_id}.extensions.{extension_id}.update')
    def put(self, queue_id, extension_id):
        queue = self.queue_dao.get(queue_id)
        extension = self.extension_dao.get(extension_id)
        self.service.associate(queue, extension)
        return '', 204
