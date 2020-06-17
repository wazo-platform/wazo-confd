# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import EndpointSIPSchema


class SipList(ListResource):

    model = EndpointSIP
    schema = EndpointSIPSchema

    def __init__(self, service, dao):
        super().__init__(service)
        self.dao = dao

    def build_headers(self, sip):
        return {'Location': url_for('endpoint_sip', uuid=sip.uuid, _external=True)}

    @required_acl('confd.endpoints.sip.read')
    def get(self):
        return super().get()

    @required_acl('confd.endpoints.sip.create')
    def post(self):
        form = self.schema().load(request.get_json())
        form = self.add_tenant_to_form(form)
        parents = []

        for parent in form['parents']:
            try:
                model = self.dao.get(parent['uuid'], tenant_uuids=[form['tenant_uuid']])
                parents.append(model)
            except NotFoundError:
                metadata = {'parents': parent}
                raise errors.param_not_found('parents', 'endpoint_sip', **metadata)

        form['parents'] = parents
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)


class SipItem(ItemResource):

    schema = EndpointSIPSchema
    has_tenant_uuid = True

    @required_acl('confd.endpoints.sip.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.endpoints.sip.{uuid}.update')
    def put(self, uuid):
        return super().put(uuid)

    @required_acl('confd.endpoints.sip.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)
