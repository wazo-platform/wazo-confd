# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.callfilter import Callfilter as CallFilter

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import CallFilterSchema


class CallFilterList(ListResource):

    model = CallFilter
    schema = CallFilterSchema

    def build_headers(self, call_filter):
        return {'Location': url_for('callfilters', id=call_filter.id, _external=True)}

    @required_acl('confd.callfilters.create')
    def post(self):
        return super(CallFilterList, self).post()

    @required_acl('confd.callfilters.read')
    def get(self):
        return super(CallFilterList, self).get()


class CallFilterItem(ItemResource):

    schema = CallFilterSchema
    has_tenant_uuid = True

    @required_acl('confd.callfilters.{id}.read')
    def get(self, id):
        return super(CallFilterItem, self).get(id)

    @required_acl('confd.callfilters.{id}.update')
    def put(self, id):
        return super(CallFilterItem, self).put(id)

    @required_acl('confd.callfilters.{id}.delete')
    def delete(self, id):
        return super(CallFilterItem, self).delete(id)
