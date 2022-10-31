# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao.resources.pjsip_transport import dao as transport_dao

from .schema import EndpointSIPSchema, TemplateSIPSchema


class BaseSIPMiddleWare:
    def __init__(self, service):
        self._service = service

    def create(self, body, tenant_uuid):
        form = self._Schema().load(body)
        form['tenant_uuid'] = tenant_uuid

        templates = []
        for template in form['templates']:
            try:
                template_model = sip_dao.get(
                    template['uuid'],
                    template=True,
                    tenant_uuids=[tenant_uuid],
                )
                templates.append(template_model)
            except NotFoundError:
                metadata = {'templates': template}
                raise errors.param_not_found('templates', 'endpoint_sip', **metadata)
        form['templates'] = templates

        if form.get('transport'):
            transport_uuid = form['transport']['uuid']
            try:
                form['transport'] = transport_dao.get(transport_uuid)
            except NotFoundError as e:
                raise errors.param_not_found('transport', 'SIPTransport', **e.metadata)

        model = EndpointSIP(**form)
        model = self._service.create(model)
        return self._Schema().dump(model)


class EndpointSIPMiddleWare(BaseSIPMiddleWare):
    _Schema = EndpointSIPSchema


class TemplateSIPMiddleWare(BaseSIPMiddleWare):
    _Schema = TemplateSIPSchema
