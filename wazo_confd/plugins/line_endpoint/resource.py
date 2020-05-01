# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class LineEndpointAssociation(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, service, line_dao, endpoint_dao):
        super().__init__()
        self.service = service
        self.line_dao = line_dao
        self.endpoint_dao = endpoint_dao

    def put(self, line_id, endpoint_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        line = self.line_dao.get(line_id, tenant_uuids=tenant_uuids)
        endpoint = self.endpoint_dao.get(endpoint_id, tenant_uuids=tenant_uuids)
        self.service.associate(line, endpoint)
        return '', 204

    def delete(self, line_id, endpoint_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        line = self.line_dao.get(line_id, tenant_uuids=tenant_uuids)
        endpoint = self.endpoint_dao.get(endpoint_id, tenant_uuids=tenant_uuids)
        self.service.dissociate(line, endpoint)
        return '', 204


class LineEndpointAssociationSip(LineEndpointAssociation):
    @required_acl('confd.lines.{line_id}.endpoints.sip.{endpoint_uuid}.update')
    def put(self, line_id, endpoint_uuid):
        return super().put(line_id, endpoint_uuid)

    @required_acl('confd.lines.{line_id}.endpoints.sip.{endpoint_uuid}.delete')
    def delete(self, line_id, endpoint_uuid):
        return super().delete(line_id, endpoint_uuid)


class LineEndpointAssociationSccp(LineEndpointAssociation):
    @required_acl('confd.lines.{line_id}.endpoints.sccp.{endpoint_id}.update')
    def put(self, line_id, endpoint_id):
        return super().put(line_id, endpoint_id)

    @required_acl('confd.lines.{line_id}.endpoints.sccp.{endpoint_id}.delete')
    def delete(self, line_id, endpoint_id):
        return super().delete(line_id, endpoint_id)


class LineEndpointAssociationCustom(LineEndpointAssociation):
    @required_acl('confd.lines.{line_id}.endpoints.custom.{endpoint_id}.update')
    def put(self, line_id, endpoint_id):
        return super().put(line_id, endpoint_id)

    @required_acl('confd.lines.{line_id}.endpoints.custom.{endpoint_id}.delete')
    def delete(self, line_id, endpoint_id):
        return super().delete(line_id, endpoint_id)
