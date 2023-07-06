# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for

from xivo_dao.alchemy.outcall import Outcall

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import OutcallSchema


class OutcallList(ListResource):
    model = Outcall
    schema = OutcallSchema
    outcall_name_fmt = 'outcall-{tenant_slug}-{outcall_id}'

    def __init__(self, tenant_dao, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant_dao = tenant_dao

    def build_headers(self, outcall):
        return {'Location': url_for('outcalls', id=outcall.id, _external=True)}

    @required_acl('confd.outcalls.create')
    def post(self):
        form = self.schema().load(request.get_json())
        form = self.add_tenant_to_form(form)

        tenant = self._tenant_dao.get(form['tenant_uuid'])
        form['name'] = self.outcall_name_fmt.format(
            tenant_slug=tenant.slug,
            outcall_id=form['id'],
        )
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)

    @required_acl('confd.outcalls.read')
    def get(self):
        return super().get()


class OutcallItem(ItemResource):
    schema = OutcallSchema
    has_tenant_uuid = True

    @required_acl('confd.outcalls.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.outcalls.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.outcalls.{id}.delete')
    def delete(self, id):
        return super().delete(id)
