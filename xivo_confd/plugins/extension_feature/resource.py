# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import ExtensionFeatureSchema


class ExtensionFeatureList(ListResource):

    schema = ExtensionFeatureSchema

    @required_acl('confd.extensions.features.read')
    def get(self):
        return super(ExtensionFeatureList, self).get()

    def post(self):
        return '', 405


class ExtensionFeatureItem(ItemResource):

    schema = ExtensionFeatureSchema

    @required_acl('confd.extensions.features.{id}.read')
    def get(self, id):
        return super(ExtensionFeatureItem, self).get(id)

    @required_acl('confd.extensions.features.{id}.update')
    def put(self, id):
        return super(ExtensionFeatureItem, self).put(id)

    def delete(self, id):
        return '', 405
