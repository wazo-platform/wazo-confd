# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import EndpointSIPSchema, MergedEndpointSIPSchema, TemplateSIPSchema


class _BaseSipList(ListResource):

    model = EndpointSIP
    schema = EndpointSIPSchema

    def __init__(self, service, dao, transport_dao):
        super().__init__(service)
        self.dao = dao
        self.transport_dao = transport_dao

    def build_headers(self, sip):
        return {'Location': url_for('endpoint_sip', uuid=sip.uuid, _external=True)}

    def get(self):
        return super().get()

    def post(self):
        form = self.schema().load(request.get_json())
        form = self.add_tenant_to_form(form)

        templates = []
        for template in form['templates']:
            try:
                model = self.dao.get(
                    template['uuid'],
                    template=True,
                    tenant_uuids=[form['tenant_uuid']],
                )
                templates.append(model)
            except NotFoundError:
                metadata = {'templates': template}
                raise errors.param_not_found('templates', 'endpoint_sip', **metadata)
        form['templates'] = templates

        if form.get('transport'):
            transport_uuid = form['transport']['uuid']
            try:
                form['transport'] = self.transport_dao.get(transport_uuid)
            except NotFoundError as e:
                raise errors.param_not_found('transport', 'SIPTransport', **e.metadata)

        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)


class _BaseSipItem(ItemResource):

    has_tenant_uuid = True

    def __init__(self, service, sip_dao, transport_dao):
        super().__init__(service)
        self.dao = sip_dao
        self.transport_dao = transport_dao

    def get(self, uuid):
        return super().get(uuid)

    def put(self, uuid):
        kwargs = self._add_tenant_uuid()
        sip = self.service.get(uuid, **kwargs)
        form = self.schema().load(request.get_json(), partial=True)

        if form.get('templates'):
            templates = []
            for template in form['templates']:
                try:
                    model = self.dao.get(template['uuid'], template=True, **kwargs)
                    templates.append(model)
                except NotFoundError:
                    metadata = {'templates': template}
                    raise errors.param_not_found(
                        'templates', 'endpoint_sip', **metadata
                    )
            form['templates'] = templates

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

    def delete(self, uuid):
        return super().delete(uuid)


class SipList(_BaseSipList):
    template = False
    schema = EndpointSIPSchema

    @required_acl('confd.endpoints.sip.read')
    def get(self):
        return super().get()

    @required_acl('confd.endpoints.sip.create')
    def post(self):
        return super().post()


class SipItem(_BaseSipItem):
    template = False
    schema = EndpointSIPSchema
    view_schemas = {
        'merged': MergedEndpointSIPSchema,
    }

    @required_acl('confd.endpoints.sip.{uuid}.read')
    def get(self, uuid):
        view = request.args.get('view')
        schema = self.view_schemas.get(view, self.schema)
        kwargs = self._add_tenant_uuid()
        model = self.service.get(uuid, **kwargs)
        return schema().dump(model)

    @required_acl('confd.endpoints.sip.{uuid}.update')
    def put(self, uuid):
        return super().put(uuid)

    @required_acl('confd.endpoints.sip.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)


class SipTemplateList(_BaseSipList):
    template = True
    schema = TemplateSIPSchema

    @required_acl('confd.endpoints.sip.templates.read')
    def get(self):
        return super().get()

    @required_acl('confd.endpoints.sip.templates.create')
    def post(self):
        return super().post()


class SipTemplateItem(_BaseSipItem):
    template = True
    schema = TemplateSIPSchema

    @required_acl('confd.endpoints.sip.templates.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.endpoints.sip.templates.{uuid}.update')
    def put(self, uuid):
        return super().put(uuid)

    @required_acl('confd.endpoints.sip.templates.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)
