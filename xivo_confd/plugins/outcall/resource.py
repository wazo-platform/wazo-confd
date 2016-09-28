# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from flask import url_for, request

from xivo_dao.alchemy.dialpattern import DialPattern
from xivo_dao.alchemy.outcall import Outcall

from .schema import OutcallSchema
from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource


def _create_patterns(form):
    return [DialPattern(**item) for item in form]


class OutcallList(ListResource):

    model = Outcall
    schema = OutcallSchema

    def build_headers(self, outcall):
        return {'Location': url_for('outcalls', id=outcall.id, _external=True)}

    @required_acl('confd.outcalls.create')
    def post(self):
        form = self.schema().load(request.get_json()).data
        if form.get('patterns'):
            form['patterns'] = _create_patterns(form['patterns'])
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model).data, 201, self.build_headers(model)

    @required_acl('confd.outcalls.read')
    def get(self):
        return super(OutcallList, self).get()


class OutcallItem(ItemResource):

    schema = OutcallSchema

    @required_acl('confd.outcalls.{id}.read')
    def get(self, id):
        return super(OutcallItem, self).get(id)

    @required_acl('confd.outcalls.{id}.update')
    def put(self, id):
        return super(OutcallItem, self).put(id)

    def parse_and_update(self, model):
        form = self.schema().load(request.get_json(), partial=True).data
        updated_fields = self.find_updated_fields(model, form)
        if form.get('patterns'):
            form['patterns'] = _create_patterns(form['patterns'])

        for name, value in form.iteritems():
            setattr(model, name, value)
        self.service.edit(model, updated_fields)

    @required_acl('confd.outcalls.{id}.delete')
    def delete(self, id):
        return super(OutcallItem, self).delete(id)
