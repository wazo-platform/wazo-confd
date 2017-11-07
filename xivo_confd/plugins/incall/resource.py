# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from flask import url_for, request

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.incall import Incall

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import IncallSchema


class IncallList(ListResource):

    model = Incall
    schema = IncallSchema

    def build_headers(self, incall):
        return {'Location': url_for('incalls', id=incall.id, _external=True)}

    @required_acl('confd.incalls.create')
    def post(self):
        schema = self.schema()
        form = schema.load(request.get_json()).data
        form['destination'] = Dialaction(**form['destination'])
        model = self.model(**form)
        model = self.service.create(model)
        return schema.dump(model).data, 201, self.build_headers(model)

    @required_acl('confd.incalls.read')
    def get(self):
        return super(IncallList, self).get()


class IncallItem(ItemResource):

    schema = IncallSchema

    @required_acl('confd.incalls.{id}.read')
    def get(self, id):
        return super(IncallItem, self).get(id)

    @required_acl('confd.incalls.{id}.update')
    def put(self, id):
        return super(IncallItem, self).put(id)

    def parse_and_update(self, model):
        form = self.schema().load(request.get_json(), partial=True).data
        updated_fields = self.find_updated_fields(model, form)
        if 'destination' in form:
            form['destination'] = Dialaction(**form['destination'])

        for name, value in form.iteritems():
            setattr(model, name, value)
        self.service.edit(model, updated_fields)

    def find_updated_fields(self, model, form):
        updated_fields = []
        for name, value in form.iteritems():
            try:
                if isinstance(value, dict):
                    if self.find_updated_fields(getattr(model, name), value):
                        updated_fields.append(name)

                elif getattr(model, name) != value:
                    updated_fields.append(name)
            except AttributeError:
                pass
        return updated_fields

    @required_acl('confd.incalls.{id}.delete')
    def delete(self, id):
        return super(IncallItem, self).delete(id)
