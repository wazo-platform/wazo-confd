# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import url_for

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
        return super(ExtensionList, self).post()


class ExtensionItem(ItemResource):

    schema = ExtensionSchema
    has_tenant_uuid = True

    @required_acl('confd.extensions.{id}.read')
    def get(self, id):
        return super(ExtensionItem, self).get(id)

    @required_acl('confd.extensions.{id}.update')
    def put(self, id):
        return super(ExtensionItem, self).put(id)

    @required_acl('confd.extensions.{id}.delete')
    def delete(self, id):
        return super(ExtensionItem, self).delete(id)
