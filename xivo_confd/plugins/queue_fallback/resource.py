# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource

from .schema import QueueFallbackSchema


class QueueFallbackList(ConfdResource):

    schema = QueueFallbackSchema

    def __init__(self, service, queue_dao):
        super(QueueFallbackList, self).__init__()
        self.service = service
        self.queue_dao = queue_dao

    @required_acl('confd.queues.{queue_id}.fallbacks.read')
    def get(self, queue_id):
        queue = self.queue_dao.get(queue_id)
        return self.schema().dump(queue.fallbacks).data

    @required_acl('confd.queues.{queue_id}.fallbacks.update')
    def put(self, queue_id):
        queue = self.queue_dao.get(queue_id)
        fallbacks = self.schema().load(request.get_json()).data
        self.service.edit(queue, fallbacks)
        return '', 204
