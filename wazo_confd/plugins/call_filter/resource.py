# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for

from xivo_dao.alchemy.callfilter import Callfilter as CallFilter

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource

from .schema import CallFilterSchema


class CallFilterList(ListResource):
    model = CallFilter
    schema = CallFilterSchema
    call_filter_name_fmt = 'callfilter-{tenant_slug}-{callfilter_uuid}'

    def __init__(self, tenant_dao, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant_dao = tenant_dao

    def build_headers(self, call_filter):
        return {'Location': url_for('callfilters', id=call_filter.id, _external=True)}

    @required_acl('confd.callfilters.create')
    def post(self):
        form = self.schema().load(request.get_json())
        form = self.add_tenant_to_form(form)

        tenant = self._tenant_dao.get(form['tenant_uuid'])
        form['name'] = self.callfilter_name_fmt.format(
            tenant_slug=tenant.slug,
            callfilter_uuid=form['uuid'],
        )
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)

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
