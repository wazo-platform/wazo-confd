# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
