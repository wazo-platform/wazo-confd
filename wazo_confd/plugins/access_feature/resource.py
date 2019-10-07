# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.accessfeatures import AccessFeatures

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import AccessFeatureSchema


class AccessFeatureList(ListResource):

    model = AccessFeatures
    schema = AccessFeatureSchema

    def build_headers(self, access_feature):
        return {
            'Location': url_for('access_features', id=access_feature.id, _external=True)
        }

    @required_acl('confd.access_features.create')
    def post(self):
        return super(AccessFeatureList, self).post()

    @required_acl('confd.access_features.read')
    def get(self):
        return super(AccessFeatureList, self).get()


class AccessFeatureItem(ItemResource):

    schema = AccessFeatureSchema

    @required_acl('confd.access_features.{id}.read')
    def get(self, id):
        return super(AccessFeatureItem, self).get(id)

    @required_acl('confd.access_features.{id}.update')
    def put(self, id):
        return super(AccessFeatureItem, self).put(id)

    @required_acl('confd.access_features.{id}.delete')
    def delete(self, id):
        return super(AccessFeatureItem, self).delete(id)
