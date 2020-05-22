# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class TrunkEndpointAssociation(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, service, trunk_dao, endpoint_dao):
        super().__init__()
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


class TrunkEndpointAssociationSip(TrunkEndpointAssociation):
    @required_acl('confd.trunks.{trunk_id}.endpoints.sip.{endpoint_id}.update')
    def put(self, trunk_id, endpoint_id):
        return super().put(trunk_id, endpoint_id)

    @required_acl('confd.trunks.{trunk_id}.endpoints.sip.{endpoint_id}.delete')
    def delete(self, trunk_id, endpoint_id):
        return super().delete(trunk_id, endpoint_id)


class TrunkEndpointAssociationCustom(TrunkEndpointAssociation):
    @required_acl('confd.trunks.{trunk_id}.endpoints.custom.{endpoint_id}.update')
    def put(self, trunk_id, endpoint_id):
        return super().put(trunk_id, endpoint_id)

    @required_acl('confd.trunks.{trunk_id}.endpoints.custom.{endpoint_id}.delete')
    def delete(self, trunk_id, endpoint_id):
        return super().delete(trunk_id, endpoint_id)


class TrunkEndpointAssociationIAX(TrunkEndpointAssociation):
    @required_acl('confd.trunks.{trunk_id}.endpoints.iax.{endpoint_id}.update')
    def put(self, trunk_id, endpoint_id):
        return super().put(trunk_id, endpoint_id)

    @required_acl('confd.trunks.{trunk_id}.endpoints.iax.{endpoint_id}.delete')
    def delete(self, trunk_id, endpoint_id):
        return super().delete(trunk_id, endpoint_id)
