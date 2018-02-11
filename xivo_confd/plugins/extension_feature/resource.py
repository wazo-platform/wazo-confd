# -*- coding: UTF-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import (
    ExtensionFeatureSchema,
    ExtensionFeaturesSchema,
)


class ExtensionFeatureList(ListResource):

    schema = ExtensionFeatureSchema

    @required_acl('confd.extensions.features.read')
    def get(self):
        return super(ExtensionFeatureList, self).get()

    @required_acl('confd.extensions.features.update')
    def put(self):
        form = ExtensionFeaturesSchema().load(request.get_json()).data
        models = []
        for feature in form['features']:
            try:
                model = self.service.get(feature['id'])
            except NotFoundError as e:
                raise errors.param_not_found('features', 'Extension', **e.metadata)

            for name, value in feature.iteritems():
                setattr(model, name, value)

            self.service.edit(model)
            models.append(model)

        self.service.edit_all(models)
        return '', 204

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
