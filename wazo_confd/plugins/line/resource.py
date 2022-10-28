# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.sccpline import SCCPLine as EndpointSCCP
from xivo_dao.alchemy.usercustom import UserCustom as EndpointCustom
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao.resources.pjsip_transport import dao as transport_dao

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource
from wazo_confd.plugins.line.schema import LineSchema, LineSchemaNullable
from wazo_confd.plugins.endpoint_sip.schema import EndpointSIPSchema
from wazo_confd.plugins.endpoint_sccp.schema import SccpSchema as EndpointSCCPSchema
from wazo_confd.plugins.endpoint_custom.schema import CustomSchema as EndpointCustomSchema


class LineList(ListResource):

    model = Line
    schema = LineSchemaNullable
    has_tenant_uuid = True

    def __init__(self, service, service_handle):
        super().__init__(service)
        self._endpoint_custom_service = service_handle.get('endpoint_custom')
        self._endpoint_sccp_service = service_handle.get('endpoint_sccp')
        self._endpoint_sip_service = service_handle.get('endpoint_sip')
        self._line_endpoint_custom_service = service_handle.get('line_endpoint_custom')
        self._line_endpoint_sccp_service = service_handle.get('line_endpoint_sccp')
        self._line_endpoint_sip_service = service_handle.get('line_endpoint_sip')

    def build_headers(self, line):
        return {'Location': url_for('lines', id=line.id, _external=True)}

    @required_acl('confd.lines.read')
    def get(self):
        return super().get()

    @required_acl('confd.lines.create')
    def post(self):
        form = self.schema().load(request.get_json())

        endpoint_sip_body = form.pop('endpoint_sip', None)
        endpoint_sccp_body = form.pop('endpoint_sccp', None)
        endpoint_custom_body = form.pop('endpoint_custom', None)

        model = self.model(**form)
        tenant_uuids = self._build_tenant_list({'recurse': True})
        model = self.service.create(model, tenant_uuids)

        if endpoint_sip_body:
            endpoint_sip_form = EndpointSIPSchema().load(endpoint_sip_body)
            templates = []
            for template in endpoint_sip_form['templates']:
                try:
                    template_model = sip_dao.get(
                        template['uuid'],
                        template=True,
                        tenant_uuids=[model.tenant_uuid],
                    )
                    templates.append(template_model)
                except NotFoundError:
                    metadata = {'templates': template}
                    raise errors.param_not_found('templates', 'endpoint_sip', **metadata)
            endpoint_sip_form['templates'] = templates

            if endpoint_sip_form.get('transport'):
                transport_uuid = endpoint_sip_form['transport']['uuid']
                try:
                    endpoint_sip_form['transport'] = transport_dao.get(transport_uuid)
                except NotFoundError as e:
                    raise errors.param_not_found('transport', 'SIPTransport', **e.metadata)
            endpoint_sip = EndpointSIP(tenant_uuid=model.tenant_uuid, **endpoint_sip_form)
            endpoint_sip = self._endpoint_sip_service.create(endpoint_sip)
            self._line_endpoint_sip_service.associate(model, endpoint_sip)
        elif endpoint_sccp_body:
            endpoint_sccp_form = EndpointSCCPSchema().load(endpoint_sccp_body)
            endpoint_sccp = EndpointSCCP(tenant_uuid=model.tenant_uuid, **endpoint_sccp_form)
            endpoint_sccp = self._endpoint_sccp_service.create(endpoint_sccp)
            self._line_endpoint_sccp_service.associate(model, endpoint_sccp)
        elif endpoint_custom_body:
            endpoint_custom_form = EndpointCustomSchema().load(endpoint_custom_body)
            endpoint_custom = EndpointCustom(tenant_uuid=model.tenant_uuid, **endpoint_custom_form)
            endpoint_custom = self._endpoint_custom_service.create(endpoint_custom)
            self._line_endpoint_custom_service.associate(model, endpoint_custom)

        return self.schema().dump(model), 201, self.build_headers(model)


class LineItem(ItemResource):

    schema = LineSchema
    has_tenant_uuid = True

    @required_acl('confd.lines.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.lines.{id}.update')
    def put(self, id):
        kwargs = self._add_tenant_uuid()
        model = self.service.get(id, **kwargs)
        self.parse_and_update(model, **kwargs)
        return '', 204

    @required_acl('confd.lines.{id}.delete')
    def delete(self, id):
        return super().delete(id)
