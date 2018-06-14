# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request, url_for

from xivo_dao.alchemy.extension import Extension

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import ExtensionSchema


class ExtensionList(ListResource):

    model = Extension
    schema = ExtensionSchema

    def build_headers(self, extension):
        return {'Location': url_for('extensions', id=extension.id, _external=True)}

    @required_acl('confd.extensions.read')
    def get(self):
        return super(ExtensionList, self).get()

    @required_acl('confd.extensions.create')
    def post(self):
        form = self.schema().load(request.get_json()).data
        model = self.model(**form)
        tenant_uuids = self._build_tenant_list({'recurse': True})
        model = self.service.create(model, tenant_uuids)
        return self.schema().dump(model).data, 201, self.build_headers(model)

    def _has_a_tenant_uuid(self):
        # The base function does not work because the tenant_uuid is not part
        # of the Extension model and is added by the dao.
        return True


class ExtensionItem(ItemResource):

    schema = ExtensionSchema
    has_tenant_uuid = True

    @required_acl('confd.extensions.{id}.read')
    def get(self, id):
        return super(ExtensionItem, self).get(id)

    @required_acl('confd.extensions.{id}.update')
    def put(self, id):
        kwargs = self._add_tenant_uuid()
        model = self.service.get(id, **kwargs)
        self.parse_and_update(model, **kwargs)
        return '', 204

    @required_acl('confd.extensions.{id}.delete')
    def delete(self, id):
        return super(ExtensionItem, self).delete(id)
