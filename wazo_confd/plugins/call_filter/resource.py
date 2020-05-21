# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.callfilter import Callfilter as CallFilter

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import CallFilterSchema


class CallFilterList(ListResource):

    model = CallFilter
    schema = CallFilterSchema

    def build_headers(self, call_filter):
        return {'Location': url_for('callfilters', id=call_filter.id, _external=True)}

    @required_acl('confd.callfilters.create')
    def post(self):
        return super().post()

    @required_acl('confd.callfilters.read')
    def get(self):
        return super().get()


class CallFilterItem(ItemResource):

    schema = CallFilterSchema
    has_tenant_uuid = True

    @required_acl('confd.callfilters.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.callfilters.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.callfilters.{id}.delete')
    def delete(self, id):
        return super().delete(id)
