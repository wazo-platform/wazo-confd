# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

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
