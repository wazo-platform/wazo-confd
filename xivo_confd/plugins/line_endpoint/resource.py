# -*- coding: UTF-8 -*-
# Copyright (C) 2015-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+


from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ConfdResource


class LineEndpointSchema(BaseSchema):
    line_id = fields.Integer()
    endpoint_id = fields.Integer()
    endpoint = fields.String()


class LineSccpSchema(LineEndpointSchema):
    links = ListLink(Link('lines',
                          field='line_id',
                          target='id'),
                     Link('endpoint_sccp',
                          field='endpoint_id',
                          target='id'))


class LineSipSchema(LineEndpointSchema):
    links = ListLink(Link('lines',
                          field='line_id',
                          target='id'),
                     Link('endpoint_sip',
                          field='endpoint_id',
                          target='id'))


class LineCustomSchema(LineEndpointSchema):
    links = ListLink(Link('lines',
                          field='line_id',
                          target='id'),
                     Link('endpoint_custom',
                          field='endpoint_id',
                          target='id'))


class LineEndpoint(ConfdResource):

    def __init__(self, service):
        super(LineEndpoint, self).__init__()
        self.service = service


class LineEndpointAssociation(LineEndpoint):

    def put(self, line_id, endpoint_id):
        line = self.service.get_line(line_id)
        endpoint = self.service.get_endpoint(endpoint_id)
        self.service.associate(line, endpoint)
        return '', 204

    def delete(self, line_id, endpoint_id):
        line = self.service.get_line(line_id)
        endpoint = self.service.get_endpoint(endpoint_id)
        self.service.dissociate(line, endpoint)
        return '', 204


class LineEndpointGet(LineEndpoint):

    def get(self, line_id):
        line_endpoint = self.service.get_association_from_line(line_id)
        return self.schema().dump(line_endpoint).data


class EndpointLineGet(LineEndpoint):

    def get(self, endpoint_id):
        line_endpoint = self.service.get_association_from_endpoint(endpoint_id)
        return self.schema().dump(line_endpoint).data


class LineEndpointAssociationSip(LineEndpointAssociation):

    @required_acl('confd.lines.{line_id}.endpoints.sip.{endpoint_id}.update')
    def put(self, line_id, endpoint_id):
        return super(LineEndpointAssociationSip, self).put(line_id, endpoint_id)

    @required_acl('confd.lines.{line_id}.endpoints.sip.{endpoint_id}.delete')
    def delete(self, line_id, endpoint_id):
        return super(LineEndpointAssociationSip, self).delete(line_id, endpoint_id)


class LineEndpointGetSip(LineEndpointGet):

    schema = LineSipSchema

    @required_acl('confd.lines.{line_id}.endpoints.sip.read')
    def get(self, line_id):
        return super(LineEndpointGetSip, self).get(line_id)


class EndpointLineGetSip(EndpointLineGet):

    schema = LineSipSchema

    @required_acl('confd.endpoints.sip.{endpoint_id}.lines.read')
    def get(self, endpoint_id):
        return super(EndpointLineGetSip, self).get(endpoint_id)


class LineEndpointAssociationSccp(LineEndpointAssociation):

    @required_acl('confd.lines.{line_id}.endpoints.sccp.{endpoint_id}.update')
    def put(self, line_id, endpoint_id):
        return super(LineEndpointAssociationSccp, self).put(line_id, endpoint_id)

    @required_acl('confd.lines.{line_id}.endpoints.sccp.{endpoint_id}.delete')
    def delete(self, line_id, endpoint_id):
        return super(LineEndpointAssociationSccp, self).delete(line_id, endpoint_id)


class LineEndpointGetSccp(LineEndpointGet):

    schema = LineSccpSchema

    @required_acl('confd.lines.{line_id}.endpoints.sccp.read')
    def get(self, line_id):
        return super(LineEndpointGetSccp, self).get(line_id)


class EndpointLineGetSccp(EndpointLineGet):

    schema = LineSccpSchema

    @required_acl('confd.endpoints.sccp.{endpoint_id}.lines.read')
    def get(self, endpoint_id):
        return super(EndpointLineGetSccp, self).get(endpoint_id)


class LineEndpointAssociationCustom(LineEndpointAssociation):

    @required_acl('confd.lines.{line_id}.endpoints.custom.{endpoint_id}.update')
    def put(self, line_id, endpoint_id):
        return super(LineEndpointAssociationCustom, self).put(line_id, endpoint_id)

    @required_acl('confd.lines.{line_id}.endpoints.custom.{endpoint_id}.delete')
    def delete(self, line_id, endpoint_id):
        return super(LineEndpointAssociationCustom, self).delete(line_id, endpoint_id)


class LineEndpointGetCustom(LineEndpointGet):

    schema = LineCustomSchema

    @required_acl('confd.lines.{line_id}.endpoints.custom.read')
    def get(self, line_id):
        return super(LineEndpointGetCustom, self).get(line_id)


class EndpointLineGetCustom(EndpointLineGet):

    schema = LineCustomSchema

    @required_acl('confd.endpoints.custom.{endpoint_id}.lines.read')
    def get(self, endpoint_id):
        return super(EndpointLineGetCustom, self).get(endpoint_id)
