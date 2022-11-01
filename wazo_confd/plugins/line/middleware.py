# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.linefeatures import LineFeatures as Line

from .schema import LineSchemaNullable


class LineMiddleWare:
    def __init__(self, service, middleware_handle):
        self._service = service
        self._schema = LineSchemaNullable()
        self._middleware_handle = middleware_handle

    def create(self, body, tenant_uuid, tenant_uuids):
        form = self._schema.load(body)

        endpoint_custom_body = form.pop('endpoint_custom', None)
        endpoint_sccp_body = form.pop('endpoint_sccp', None)
        endpoint_sip_body = form.pop('endpoint_sip', None)

        caller_id_name = form.pop('caller_id_name')

        model = Line(**form)
        model = self._service.create(model, tenant_uuids)

        if endpoint_sip_body:
            endpoint_sip_middleware = self._middleware_handle.get('endpoint_sip')
            endpoint_sip = endpoint_sip_middleware.create(
                endpoint_sip_body,
                tenant_uuid,
            )
            line_endpoint_sip_middleware = self._middleware_handle.get(
                'line_endpoint_sip'
            )
            line_endpoint_sip_middleware.associate(
                model.id,
                endpoint_sip['uuid'],
                tenant_uuids,
            )
        elif endpoint_sccp_body:
            endpoint_sccp_middleware = self._middleware_handle.get('endpoint_sccp')
            endpoint_sccp = endpoint_sccp_middleware.create(
                endpoint_sccp_body,
                tenant_uuid,
            )
            line_endpoint_sccp_middleware = self._middleware_handle.get(
                'line_endpoint_sccp',
            )
            line_endpoint_sccp_middleware.associate(
                model.id,
                endpoint_sccp['id'],
                tenant_uuids,
            )
        elif endpoint_custom_body:
            endpoint_custom_middleware = self._middleware_handle.get('endpoint_custom')
            endpoint_custom = endpoint_custom_middleware.create(
                endpoint_custom_body,
                tenant_uuid,
            )
            line_endpoint_custom_middleware = self._middleware_handle.get(
                'line_endpoint_custom',
            )
            line_endpoint_custom_middleware.associate(
                model.id,
                endpoint_custom['id'],
                tenant_uuids,
            )

        if caller_id_name:
            model.caller_id_name = caller_id_name
            self._service.edit(model, tenant_uuids=None)

        updated_model = self._service.get(model.id)
        line_response = self._schema.dump(updated_model)

        return line_response
