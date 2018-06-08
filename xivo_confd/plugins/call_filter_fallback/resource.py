# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource

from .schema import CallFilterFallbackSchema


class CallFilterFallbackList(ConfdResource):

    schema = CallFilterFallbackSchema

    def __init__(self, service, call_filter_dao):
        super(CallFilterFallbackList, self).__init__()
        self.service = service
        self.call_filter_dao = call_filter_dao

    @required_acl('confd.callfilters.{call_filter_id}.fallbacks.read')
    def get(self, call_filter_id):
        call_filter = self.call_filter_dao.get(call_filter_id)
        return self.schema().dump(call_filter.fallbacks).data

    @required_acl('confd.callfilters.{call_filter_id}.fallbacks.update')
    def put(self, call_filter_id):
        call_filter = self.call_filter_dao.get(call_filter_id)
        fallbacks = self.schema().load(request.get_json()).data
        self.service.edit(call_filter, fallbacks)
        return '', 204
