# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_confd import api
from xivo_confd.plugins.line_endpoint.resource import LineEndpointAssociationSip
from xivo_confd.plugins.line_endpoint.resource import LineEndpointGetSip
from xivo_confd.plugins.line_endpoint.resource import EndpointLineGetSip
from xivo_confd.plugins.line_endpoint.resource import LineEndpointAssociationSccp
from xivo_confd.plugins.line_endpoint.resource import LineEndpointGetSccp
from xivo_confd.plugins.line_endpoint.resource import EndpointLineGetSccp
from xivo_confd.plugins.line_endpoint.resource import LineEndpointAssociationCustom
from xivo_confd.plugins.line_endpoint.resource import LineEndpointGetCustom
from xivo_confd.plugins.line_endpoint.resource import EndpointLineGetCustom

from xivo_confd.plugins.endpoint_sccp.service import build_service as build_sccp_service
from xivo_confd.plugins.endpoint_sip.service import build_service as build_sip_service
from xivo_confd.plugins.endpoint_custom.service import build_service as build_custom_service
from xivo_confd.plugins.line_endpoint.service import build_service


class Plugin(object):

    def load(self, core):
        provd_client = core.provd_client()

        self.load_sip(provd_client)
        self.load_sccp(provd_client)
        self.load_custom(provd_client)

    def load_sip(self, provd_client):
        service = self.build_sip_service(provd_client)

        api.add_resource(LineEndpointAssociationSip,
                         '/lines/<int:line_id>/endpoints/sip/<int:endpoint_id>',
                         endpoint='line_endpoint_sip',
                         resource_class_args=(service,))

        api.add_resource(LineEndpointGetSip,
                         '/lines/<int:line_id>/endpoints/sip',
                         resource_class_args=(service,))

        api.add_resource(EndpointLineGetSip,
                         '/endpoints/sip/<int:endpoint_id>/lines',
                         resource_class_args=(service,))

    def load_sccp(self, provd_client):
        service = self.build_sccp_service(provd_client)

        api.add_resource(LineEndpointAssociationSccp,
                         '/lines/<int:line_id>/endpoints/sccp/<int:endpoint_id>',
                         endpoint='line_endpoint_sccp',
                         resource_class_args=(service,))

        api.add_resource(LineEndpointGetSccp,
                         '/lines/<int:line_id>/endpoints/sccp',
                         resource_class_args=(service,))

        api.add_resource(EndpointLineGetSccp,
                         '/endpoints/sccp/<int:endpoint_id>/lines',
                         resource_class_args=(service,))

    def load_custom(self, provd_client):
        service = self.build_custom_service(provd_client)

        api.add_resource(LineEndpointAssociationCustom,
                         '/lines/<int:line_id>/endpoints/custom/<int:endpoint_id>',
                         endpoint='line_endpoint_custom',
                         resource_class_args=(service,))

        api.add_resource(LineEndpointGetCustom,
                         '/lines/<int:line_id>/endpoints/custom',
                         resource_class_args=(service,))

        api.add_resource(EndpointLineGetCustom,
                         '/endpoints/custom/<int:endpoint_id>/lines',
                         resource_class_args=(service,))

    def build_sip_service(self, provd_client):
        sip_service = build_sip_service(provd_client)
        return build_service(provd_client, 'sip', sip_service)

    def build_sccp_service(self, provd_client):
        sccp_service = build_sccp_service()
        return build_service(provd_client, 'sccp', sccp_service)

    def build_custom_service(self, provd_client):
        custom_service = build_custom_service()
        return build_service(provd_client, 'custom', custom_service)
