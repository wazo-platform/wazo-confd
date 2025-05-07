# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for
from xivo_dao.alchemy.pjsip_transport import PJSIPTransport

from wazo_confd.auth import required_acl, required_master_tenant
from wazo_confd.helpers.asterisk import AsteriskConfigurationList
from wazo_confd.helpers.restful import ConfdResource, ItemResource, ListResource

from .schema import PJSIPTransportDeleteRequestSchema, PJSIPTransportSchema


class PJSIPDocList(ConfdResource):
    def __init__(self, pjsip_doc):
        self._pjsip_doc = pjsip_doc

    @required_acl('confd.asterisk.pjsip.doc.read')
    def get(self):
        return self._pjsip_doc.get()


class PJSIPGlobalList(AsteriskConfigurationList):
    section_name = 'global'

    @required_master_tenant()
    @required_acl('confd.asterisk.pjsip.global.read')
    def get(self):
        return super().get()

    @required_master_tenant()
    @required_acl('confd.asterisk.pjsip.global.update')
    def put(self):
        return super().put()


class PJSIPSystemList(AsteriskConfigurationList):
    section_name = 'system'

    @required_master_tenant()
    @required_acl('confd.asterisk.pjsip.system.read')
    def get(self):
        return super().get()

    @required_master_tenant()
    @required_acl('confd.asterisk.pjsip.system.update')
    def put(self):
        return super().put()


class PJSIPTransportList(ListResource):
    schema = PJSIPTransportSchema
    model = PJSIPTransport

    def __init__(self, service):
        self.service = service

    def build_headers(self, transport):
        return {
            'Location': url_for(
                'sip_transports',
                transport_uuid=transport.uuid,
                _external=True,
            )
        }

    @required_acl('confd.sip.transports.read')
    def get(self):
        return super().get()

    @required_master_tenant()
    @required_acl('confd.sip.transports.create')
    def post(self):
        return super().post()


class PJSIPTransportItem(ItemResource):
    schema = PJSIPTransportSchema

    def __init__(self, service):
        self.service = service

    @required_acl('confd.sip.transports.{transport_uuid}.read')
    def get(self, transport_uuid):
        return super().get(transport_uuid)

    @required_master_tenant()
    @required_acl('confd.sip.transports.{transport_uuid}.update')
    def put(self, transport_uuid):
        return super().put(transport_uuid)

    @required_master_tenant()
    @required_acl('confd.sip.transports.{transport_uuid}.delete')
    def delete(self, transport_uuid):
        transport = self.service.get(transport_uuid)
        params = PJSIPTransportDeleteRequestSchema().load(request.args)
        fallback = params['fallback']
        if fallback:
            fallback = self.service.get(fallback)
        self.service.delete(transport, fallback=fallback)
        return '', 204
