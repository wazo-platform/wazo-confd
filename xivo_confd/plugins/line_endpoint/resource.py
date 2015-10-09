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
    'sip_id': fields.Integer,
    'links': FieldList(Link('lines',
                            field='line_id',
                            target='id'),
                       Link('endpoint_sip',
                            field='sip_id',
                            target='id'))
}


class LineEndpoint(ConfdResource):

    def __init__(self, service):
        super(LineEndpoint, self).__init__()
        self.service = service


class LineEndpointAssociation(LineEndpoint):

    def put(self, line_id, endpoint_id):
        line = self.service.get_line(line_id)
        sip = self.service.get_sip(endpoint_id)
        self.service.associate(line, sip)
        return '', 204

    def delete(self, line_id, endpoint_id):
        line = self.service.get_line(line_id)
        sip = self.service.get_sip(endpoint_id)
        self.service.dissociate(line, sip)
        return '', 204


class LineEndpointGet(LineEndpoint):

    @marshal_with(fields)
    def get(self, line_id):
        line_endpoint = self.service.get_association_from_line(line_id)
        return line_endpoint


class EndpointLineGet(LineEndpoint):

    @marshal_with(fields)
    def get(self, endpoint_id):
        line_endpoint = self.service.get_association_from_endpoint(endpoint_id)
        return line_endpoint
