# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import url_for

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource
from xivo_confd.plugins.line.schema import LineSchema, LineSchemaNullable
from xivo_dao.alchemy.linefeatures import LineFeatures as Line


class LineList(ListResource):

    model = Line
    schema = LineSchemaNullable

    def build_headers(self, line):
        return {'Location': url_for('lines', id=line.id, _external=True)}

    @required_acl('confd.lines.read')
    def get(self):
        return super(LineList, self).get()

    @required_acl('confd.lines.create')
    def post(self):
        return super(LineList, self).post()


class LineItem(ItemResource):

    schema = LineSchema

    @required_acl('confd.lines.{id}.read')
    def get(self, id):
        return super(LineItem, self).get(id)

    @required_acl('confd.lines.{id}.update')
    def put(self, id):
        return super(LineItem, self).put(id)

    @required_acl('confd.lines.{id}.delete')
    def delete(self, id):
        return super(LineItem, self).delete(id)
