# Copyright 2021-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for

from xivo_dao.alchemy.ingress_http import IngressHTTP

from wazo_confd.auth import required_acl, master_tenant_uuid
from wazo_confd.helpers.restful import ItemResource, ListResource

from .schema import ExtraParamsSchema, IngressHTTPSchema


class IngressHTTPList(ListResource):
    model = IngressHTTP
    schema = IngressHTTPSchema

    def build_headers(self, ingress_http):
        return {
            'Location': url_for(
                'ingresses_http', uuid=ingress_http.uuid, _external=True
            )
        }

    @required_acl('confd.ingresses.http.create')
    def post(self):
        return super().post()

    @required_acl('confd.ingresses.http.read')
    def get(self):
        result = super().get()

        if result.get('total') > 0:
            return result
        else:
            extra_params = ExtraParamsSchema().load(request.args)
            if extra_params.get('fallback'):
                return super().unsafe_fallback_get([str(master_tenant_uuid)])
            else:
                return result


class IngressHTTPItem(ItemResource):
    schema = IngressHTTPSchema
    has_tenant_uuid = True

    @required_acl('confd.ingresses.http.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.ingresses.http.{uuid}.update')
    def put(self, uuid):
        return super().put(uuid)

    @required_acl('confd.ingresses.http.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)
