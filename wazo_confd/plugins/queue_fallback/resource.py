# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource

from .schema import QueueFallbackSchema


class QueueFallbackList(ConfdResource):

    schema = QueueFallbackSchema
    has_tenant_uuid = True

    def __init__(self, service, queue_dao):
        super(QueueFallbackList, self).__init__()
        self.service = service
        self.queue_dao = queue_dao

    @required_acl('confd.queues.{queue_id}.fallbacks.read')
    def get(self, queue_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        queue = self.queue_dao.get(queue_id, tenant_uuids=tenant_uuids)
        return self.schema().dump(queue.fallbacks).data

    @required_acl('confd.queues.{queue_id}.fallbacks.update')
    def put(self, queue_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        queue = self.queue_dao.get(queue_id, tenant_uuids=tenant_uuids)
        fallbacks = self.schema().load(request.get_json()).data
        self.service.edit(queue, fallbacks)
        return '', 204
