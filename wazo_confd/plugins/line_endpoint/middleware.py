# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.endpoint_sip import dao as endpoint_sip_dao
from xivo_dao.resources.endpoint_sccp import dao as endpoint_sccp_dao
from xivo_dao.resources.endpoint_custom import dao as endpoint_custom_dao


class _BaseLineEndpointMiddleWare:
    def __init__(self, service):
        self._service = service

    def associate(self, line_id, endpoint_id, tenant_uuids):
        line = line_dao.get(line_id, tenant_uuids=tenant_uuids)
        endpoint = self._get_endpoint(endpoint_id, tenant_uuids)
        self._service.associate(line, endpoint)

    def dissociate(self, line_id, endpoint_id, tenant_uuids):
        line = line_dao.get(line_id, tenant_uuids=tenant_uuids)
        endpoint = self._get_endpoint(endpoint_id, tenant_uuids)
        self._service.dissociate(line, endpoint)


class LineEndpointSIPMiddleWare(_BaseLineEndpointMiddleWare):
    def _get_endpoint(self, endpoint_uuid, tenant_uuids):
        return endpoint_sip_dao.get(
            endpoint_uuid,
            template=False,
            tenant_uuids=tenant_uuids,
        )


class LineEndpointSCCPMiddleWare(_BaseLineEndpointMiddleWare):
    def _get_endpoint(self, endpoint_id, tenant_uuids):
        return endpoint_sccp_dao.get(
            endpoint_id,
            tenant_uuids=tenant_uuids,
        )


class LineEndpointCustomMiddleWare(_BaseLineEndpointMiddleWare):
    def _get_endpoint(self, endpoint_id, tenant_uuids):
        return endpoint_custom_dao.get(
            endpoint_id,
            tenant_uuids=tenant_uuids,
        )
