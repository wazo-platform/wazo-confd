# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ConfdResource


class TrunkEndpointSchema(BaseSchema):
    trunk_id = fields.Integer()
    endpoint = fields.String()
    endpoint_id = fields.Integer()


class TrunkEndpointSipSchema(TrunkEndpointSchema):
    links = ListLink(Link('trunks',
                          field='trunk_id',
                          target='id'),
                     Link('endpoint_sip',
                          field='endpoint_id',
                          target='id'))


class TrunkEndpointCustomSchema(TrunkEndpointSchema):
    links = ListLink(Link('trunks',
                          field='trunk_id',
                          target='id'),
                     Link('endpoint_custom',
                          field='endpoint_id',
                          target='id'))


class TrunkEndpoint(ConfdResource):

    def __init__(self, service):
        super(TrunkEndpoint, self).__init__()
        self.service = service


class TrunkEndpointAssociation(TrunkEndpoint):

    def put(self, trunk_id, endpoint_id):
        trunk = self.service.get_trunk(trunk_id)
        endpoint = self.service.get_endpoint(endpoint_id)
        self.service.associate(trunk, endpoint)
        return '', 204

    def delete(self, trunk_id, endpoint_id):
        trunk = self.service.get_trunk(trunk_id)
        endpoint = self.service.get_endpoint(endpoint_id)
        self.service.dissociate(trunk, endpoint)
        return '', 204


class TrunkEndpointGet(TrunkEndpoint):

    def get(self, trunk_id):
        trunk_endpoint = self.service.get_association_from_trunk(trunk_id)
        return self.schema().dump(trunk_endpoint).data


class EndpointTrunkGet(TrunkEndpoint):

    def get(self, endpoint_id):
        trunk_endpoint = self.service.get_association_from_endpoint(endpoint_id)
        return self.schema().dump(trunk_endpoint).data


class TrunkEndpointAssociationSip(TrunkEndpointAssociation):

    @required_acl('confd.trunks.{trunk_id}.endpoints.sip.{endpoint_id}.update')
    def put(self, trunk_id, endpoint_id):
        return super(TrunkEndpointAssociationSip, self).put(trunk_id, endpoint_id)

    @required_acl('confd.trunks.{trunk_id}.endpoints.sip.{endpoint_id}.delete')
    def delete(self, trunk_id, endpoint_id):
        return super(TrunkEndpointAssociationSip, self).delete(trunk_id, endpoint_id)


class TrunkEndpointGetSip(TrunkEndpointGet):
    schema = TrunkEndpointSipSchema

    @required_acl('confd.trunks.{trunk_id}.endpoints.sip.read')
    def get(self, trunk_id):
        return super(TrunkEndpointGetSip, self).get(trunk_id)


class EndpointTrunkGetSip(EndpointTrunkGet):
    schema = TrunkEndpointSipSchema

    @required_acl('confd.endpoints.sip.{endpoint_id}.trunks.read')
    def get(self, endpoint_id):
        return super(EndpointTrunkGetSip, self).get(endpoint_id)


class TrunkEndpointAssociationCustom(TrunkEndpointAssociation):

    @required_acl('confd.trunks.{trunk_id}.endpoints.custom.{endpoint_id}.update')
    def put(self, trunk_id, endpoint_id):
        return super(TrunkEndpointAssociationCustom, self).put(trunk_id, endpoint_id)

    @required_acl('confd.trunks.{trunk_id}.endpoints.custom.{endpoint_id}.delete')
    def delete(self, trunk_id, endpoint_id):
        return super(TrunkEndpointAssociationCustom, self).delete(trunk_id, endpoint_id)


class TrunkEndpointGetCustom(TrunkEndpointGet):
    schema = TrunkEndpointCustomSchema

    @required_acl('confd.trunks.{trunk_id}.endpoints.custom.read')
    def get(self, trunk_id):
        return super(TrunkEndpointGetCustom, self).get(trunk_id)


class EndpointTrunkGetCustom(EndpointTrunkGet):
    schema = TrunkEndpointCustomSchema

    @required_acl('confd.endpoints.custom.{endpoint_id}.trunks.read')
    def get(self, endpoint_id):
        return super(EndpointTrunkGetCustom, self).get(endpoint_id)
