# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource

from .schema import ContextRangeSchema, ListSchema


class ContextRangeList(ListResource):
    schema = ContextRangeSchema
    has_tenant_uuid = True

    def get(self, context_id, range_type):
        params = self.search_params()
        tenant_uuids = self._build_tenant_list({'recurse': True})

        if tenant_uuids is not None:
            params['tenant_uuids'] = tenant_uuids

        total, items = self.service.search(context_id, range_type, **params)
        return {'total': total, 'items': self.schema().dump(items, many=True)}

    def search_params(self):
        return ListSchema().load(request.args)


class ContextUserRangeList(ContextRangeList):
    @required_acl('confd.contexts.{context_id}.ranges.user.read')
    def get(self, context_id):
        return super().get(context_id, 'user')


class ContextGroupRangeList(ContextRangeList):
    @required_acl('confd.contexts.{context_id}.ranges.group.read')
    def get(self, context_id):
        return super().get(context_id, 'group')


class ContextQueueRangeList(ContextRangeList):
    @required_acl('confd.contexts.{context_id}.ranges.queue.read')
    def get(self, context_id):
        return super().get(context_id, 'queue')


class ContextConferenceRangeList(ContextRangeList):
    @required_acl('confd.contexts.{context_id}.ranges.conference.read')
    def get(self, context_id):
        return super().get(context_id, 'conference')


class ContextIncallRangeList(ContextRangeList):
    @required_acl('confd.contexts.{context_id}.ranges.incall.read')
    def get(self, context_id):
        return super().get(context_id, 'incall')
