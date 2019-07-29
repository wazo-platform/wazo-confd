# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource

from .schema import CallFilterFallbackSchema


class CallFilterFallbackList(ConfdResource):

    schema = CallFilterFallbackSchema
    has_tenant_uuid = True

    def __init__(self, service, call_filter_dao):
        super(CallFilterFallbackList, self).__init__()
        self.service = service
        self.call_filter_dao = call_filter_dao

    @required_acl('confd.callfilters.{call_filter_id}.fallbacks.read')
    def get(self, call_filter_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        call_filter = self.call_filter_dao.get(call_filter_id, tenant_uuids=tenant_uuids)
        return self.schema().dump(call_filter.fallbacks)

    @required_acl('confd.callfilters.{call_filter_id}.fallbacks.update')
    def put(self, call_filter_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        call_filter = self.call_filter_dao.get(call_filter_id, tenant_uuids=tenant_uuids)
        fallbacks = self.schema().load(request.get_json())
        self.service.edit(call_filter, fallbacks)
        return '', 204
