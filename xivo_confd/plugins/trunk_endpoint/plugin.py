# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao.resources.endpoint_sip import dao as endpoint_sip_dao
from xivo_dao.resources.endpoint_custom import dao as endpoint_custom_dao

from xivo_confd import api
from .service import build_service
from .resource import (TrunkEndpointAssociationSip,
                       TrunkEndpointGetSip,
                       EndpointTrunkGetSip,
                       TrunkEndpointAssociationCustom,
                       TrunkEndpointGetCustom,
                       EndpointTrunkGetCustom)


class Plugin(object):

    def load(self, core):
        self.load_sip()
        self.load_custom()

    def load_sip(self):
        service = self.build_sip_service()

        api.add_resource(TrunkEndpointAssociationSip,
                         '/trunks/<int:trunk_id>/endpoints/sip/<int:endpoint_id>',
                         endpoint='trunk_endpoint_sip',
                         resource_class_args=(service,))

        api.add_resource(TrunkEndpointGetSip,
                         '/trunks/<int:trunk_id>/endpoints/sip',
                         resource_class_args=(service,))

        api.add_resource(EndpointTrunkGetSip,
                         '/endpoints/sip/<int:endpoint_id>/trunks',
                         resource_class_args=(service,))

    def load_custom(self):
        service = self.build_custom_service()

        api.add_resource(TrunkEndpointAssociationCustom,
                         '/trunks/<int:trunk_id>/endpoints/custom/<int:endpoint_id>',
                         endpoint='trunk_endpoint_custom',
                         resource_class_args=(service,))

        api.add_resource(TrunkEndpointGetCustom,
                         '/trunks/<int:trunk_id>/endpoints/custom',
                         resource_class_args=(service,))

        api.add_resource(EndpointTrunkGetCustom,
                         '/endpoints/custom/<int:endpoint_id>/trunks',
                         resource_class_args=(service,))

    def build_sip_service(self):
        return build_service('sip', endpoint_sip_dao)

    def build_custom_service(self):
        return build_service('custom', endpoint_custom_dao)
