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

    def __init__(self, service, dao, transport_dao):
        super().__init__(service)
        self.dao = dao
        self.transport_dao = transport_dao

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
                raise errors.param_not_found('parents', 'EndpointSIP', **metadata)

        if form.get('transport'):
            transport_uuid = form['transport']['uuid']
            try:
                # TODO pass object
                self.transport_dao.get(transport_uuid)
            except NotFoundError as e:
                raise errors.param_not_found('transport', 'SIPTransport', **e.metadata)

        form['parents'] = parents
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)


class SipItem(ItemResource):

    schema = EndpointSIPSchema
    has_tenant_uuid = True

    def __init__(self, service, transport_dao):
        super().__init__(service)
        self.transport_dao = transport_dao

    @required_acl('confd.endpoints.sip.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.endpoints.sip.{uuid}.update')
    def put(self, uuid):
        kwargs = self._add_tenant_uuid()
        sip = self.service.get(uuid, **kwargs)
        form = self.schema().load(request.get_json(), partial=True)
        if form.get('transport'):
            transport_uuid = form['transport']['uuid']
            try:
                form['transport'] = self.transport_dao.get(transport_uuid)
            except NotFoundError as e:
                raise errors.param_not_found('transport', 'SIPTransport', **e.metadata)
        for name, value in form.items():
            setattr(sip, name, value)
        self.service.edit(sip)
        return '', 204

    @required_acl('confd.endpoints.sip.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)
