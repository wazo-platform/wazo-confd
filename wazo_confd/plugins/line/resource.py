# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from xivo_dao.alchemy.linefeatures import LineFeatures as Line

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource
from wazo_confd.plugins.line.schema import LineSchema, LineSchemaNullable

from wazo_confd.plugins.endpoint_custom.resource import CustomList
from wazo_confd.plugins.endpoint_sccp.resource import SccpList
from wazo_confd.plugins.endpoint_sip.resource import SipList
from wazo_confd.plugins.line_endpoint.resource import (
    LineEndpointAssociationCustom,
    LineEndpointAssociationSccp,
    LineEndpointAssociationSip,
)


class LineList(ListResource):

    model = Line
    schema = LineSchemaNullable
    has_tenant_uuid = True

    def __init__(
        self,
        line_service,
        endpoint_custom_service,
        endpoint_sip_service,
        line_endpoint_custom_association_service,
        line_endpoint_sip_association_service,
        line_endpoint_sccp_association_service,
        endpoint_sccp_service,
        endpoint_custom_dao,
        endpoint_sccp_dao,
        line_dao,
        sip_dao,
        transport_dao,
    ):
        super().__init__(line_service)
        self._endpoint_sip_list_resource = SipList(
            endpoint_sip_service, sip_dao, transport_dao
        )
        self._endpoint_sccp_list_resource = SccpList(
            endpoint_sccp_service,
        )
        self._endpoint_custom_list_resource = CustomList(
            endpoint_custom_service,
        )
        self._line_endpoint_custom_association_resource = LineEndpointAssociationCustom(
            line_endpoint_custom_association_service, line_dao, endpoint_custom_dao,
        )
        self._line_endpoint_sip_association_resource = LineEndpointAssociationSip(
            line_endpoint_sip_association_service, line_dao, sip_dao
        )
        self._line_endpoint_sccp_association_resource = LineEndpointAssociationSccp(
            line_endpoint_sccp_association_service, line_dao, endpoint_sccp_dao,
        )

    def build_headers(self, line):
        return {'Location': url_for('lines', id=line.id, _external=True)}

    @required_acl('confd.lines.read')
    def get(self):
        return super().get()

    @required_acl('confd.lines.create')
    def post(self):
        return super().post()

    def _post(self, item):
        form = self.schema().load(item)

        endpoint_sip_body = form.pop('endpoint_sip', None)
        endpoint_sccp_body = form.pop('endpoint_sccp', None)
        endpoint_custom_body = form.pop('endpoint_custom', None)
        extensions = form.pop('extensions', None) or []

        model = self.model(**form)
        tenant_uuids = self._build_tenant_list({'recurse': True})
        model = self.service.create(model, tenant_uuids)

        payload = self.schema().dump(model)

        if endpoint_sip_body:
            endpoint_sip, _, _ = self._endpoint_sip_list_resource._post(
                endpoint_sip_body
            )
            self._line_endpoint_sip_association_resource.put(
                model.id,
                endpoint_sip['uuid'],
            )
            payload['endpoint_sip'] = endpoint_sip
        elif endpoint_sccp_body:
            endpoint_sccp, _, _ = self._endpoint_sccp_list_resource._post(
                endpoint_sccp_body
            )
            self._line_endpoint_sccp_association_resource.put(
                model.id,
                endpoint_sccp['id'],
            )
            payload['endpoint_sccp'] = endpoint_sccp
        elif endpoint_custom_body:
            endpoint_custom, _, _ = self._endpoint_custom_list_resource._post(
                endpoint_custom_body
            )
            self._line_endpoint_custom_association_resource.put(
                model.id,
                endpoint_custom['id'],
            )
            payload['endpoint_custom'] = endpoint_custom

        return payload, 201, self.build_headers(model)


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


# class LineListV2(ListResource):

#     api_version = '2.0'

#     model = Line
#     schema = LineSchemaNullable
#     has_tenant_uuid = True

#     def __init__(self, line_service, extension_service):
#         super().__init__(line_service)
#         self._extension_list_resource = ExtensionList(extension_service, json_path='lines.extension')

#     def build_headers(self, line):
#         return {'Location': url_for('lines', id=line.id, _external=True)}

#     @required_acl('confd.lines.create')
#     def post(self):
#         if self._many:
#             body = self.find_json_sub_dict(self.json_path, request.get_json())
#         else:
#             body = [self.find_json_sub_dict(self.json_path, request.get_json())]

#         results = []
#         headers = None
#         for item in body:
#             form = self.schema().load(item)
#             model = self.model(**form)
#             tenant_uuids = self._build_tenant_list({'recurse': True})
#             model = self.service.create(model, tenant_uuids)
#             results.append(self.schema().dump(model))
#             if not headers:
#                 headers = self.build_headers(model)

#         if self._many:
#             return results, 201, headers
#         else:
#             return results[0], 201, headers
