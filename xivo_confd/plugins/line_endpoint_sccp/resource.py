# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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


from flask_restful import fields, marshal_with

from xivo_confd.helpers.restful import ConfdResource, Link, FieldList

fields = {
    'line_id': fields.Integer,
    'sccp_id': fields.Integer,
    'links': FieldList(Link('lines',
                            field='line_id',
                            target='id'),
                       Link('endpoint_sccp',
                            field='sccp_id',
                            target='id'))
}


class LineEndpointSccp(ConfdResource):

    def __init__(self, service):
        super(LineEndpointSccp, self).__init__()
        self.service = service


class LineEndpointSccpAssociation(LineEndpointSccp):

    def put(self, line_id, endpoint_id):
        line = self.service.get_line(line_id)
        sccp = self.service.get_sccp(endpoint_id)
        self.service.associate(line, sccp)
        return '', 204

    def delete(self, line_id, endpoint_id):
        line = self.service.get_line(line_id)
        sccp = self.service.get_sccp(endpoint_id)
        self.service.dissociate(line, sccp)
        return '', 204


class LineEndpointSccpGet(LineEndpointSccp):

    @marshal_with(fields)
    def get(self, line_id):
        line_endpoint = self.service.get_association_from_line(line_id)
        return line_endpoint


class EndpointSccpLineGet(LineEndpointSccp):

    @marshal_with(fields)
    def get(self, endpoint_id):
        line_endpoint = self.service.get_association_from_endpoint(endpoint_id)
        return line_endpoint
