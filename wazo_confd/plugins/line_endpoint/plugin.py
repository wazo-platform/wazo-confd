# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.endpoint_custom import dao as endpoint_custom_dao
from xivo_dao.resources.endpoint_sccp import dao as endpoint_sccp_dao
from xivo_dao.resources.endpoint_sip import dao as endpoint_sip_dao
from xivo_dao.resources.line import dao as line_dao

from wazo_provd_client import Client as ProvdClient

from .resource import (
    LineEndpointAssociationSip,
    LineEndpointAssociationSccp,
    LineEndpointAssociationCustom,
)
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        self.load_sip(api, provd_client)
        self.load_sccp(api, provd_client)
        self.load_custom(api, provd_client)

    def load_sip(self, api, provd_client):
        service = self.build_sip_service(provd_client)

        api.add_resource(
            LineEndpointAssociationSip,
            '/lines/<int:line_id>/endpoints/sip/<int:endpoint_id>',
            endpoint='line_endpoint_sip',
            resource_class_args=(service, line_dao, endpoint_sip_dao),
        )

    def load_sccp(self, api, provd_client):
        service = self.build_sccp_service(provd_client)

        api.add_resource(
            LineEndpointAssociationSccp,
            '/lines/<int:line_id>/endpoints/sccp/<int:endpoint_id>',
            endpoint='line_endpoint_sccp',
            resource_class_args=(service, line_dao, endpoint_sccp_dao),
        )

    def load_custom(self, api, provd_client):
        service = self.build_custom_service(provd_client)

        api.add_resource(
            LineEndpointAssociationCustom,
            '/lines/<int:line_id>/endpoints/custom/<int:endpoint_id>',
            endpoint='line_endpoint_custom',
            resource_class_args=(service, line_dao, endpoint_custom_dao),
        )

    def build_sip_service(self, provd_client):
        return build_service(provd_client, 'sip')

    def build_sccp_service(self, provd_client):
        return build_service(provd_client, 'sccp')

    def build_custom_service(self, provd_client):
        return build_service(provd_client, 'custom')
