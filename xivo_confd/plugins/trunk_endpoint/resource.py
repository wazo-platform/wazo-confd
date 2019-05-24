# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from xivo_confd.auth import required_acl
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

    has_tenant_uuid = True

    def __init__(self, service, trunk_dao, endpoint_dao):
        super(TrunkEndpointAssociation, self).__init__(service)
        self.service = service
        self.trunk_dao = trunk_dao
        self.endpoint_dao = endpoint_dao

    def put(self, trunk_id, endpoint_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        trunk = self.trunk_dao.get(trunk_id, tenant_uuids=tenant_uuids)
        endpoint = self.endpoint_dao.get(endpoint_id, tenant_uuids=tenant_uuids)
        self.service.associate(trunk, endpoint)
        return '', 204

    def delete(self, trunk_id, endpoint_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        trunk = self.trunk_dao.get(trunk_id, tenant_uuids=tenant_uuids)
        endpoint = self.endpoint_dao.get(endpoint_id, tenant_uuids=tenant_uuids)
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


class TrunkEndpointAssociationIAX(TrunkEndpointAssociation):

    @required_acl('confd.trunks.{trunk_id}.endpoints.iax.{endpoint_id}.update')
    def put(self, trunk_id, endpoint_id):
        return super(TrunkEndpointAssociationIAX, self).put(trunk_id, endpoint_id)

    @required_acl('confd.trunks.{trunk_id}.endpoints.iax.{endpoint_id}.delete')
    def delete(self, trunk_id, endpoint_id):
        return super(TrunkEndpointAssociationIAX, self).delete(trunk_id, endpoint_id)
