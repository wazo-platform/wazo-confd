# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.endpoint_custom import dao as endpoint_custom_dao
from xivo_dao.resources.endpoint_iax import dao as endpoint_iax_dao
from xivo_dao.resources.endpoint_sip import dao as endpoint_sip_dao
from xivo_dao.resources.trunk import dao as trunk_dao

from .resource import (
    TrunkEndpointAssociationCustom,
    TrunkEndpointAssociationSip,
    TrunkEndpointAssociationIAX,
)
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        self.load_sip(api)
        self.load_custom(api)
        self.load_iax(api)

    def load_sip(self, api):
        service = build_service('sip')

        api.add_resource(
            TrunkEndpointAssociationSip,
            '/trunks/<int:trunk_id>/endpoints/sip/<int:endpoint_id>',
            endpoint='trunk_endpoint_sip',
            resource_class_args=(service, trunk_dao, endpoint_sip_dao),
        )

    def load_custom(self, api):
        service = build_service('custom')

        api.add_resource(
            TrunkEndpointAssociationCustom,
            '/trunks/<int:trunk_id>/endpoints/custom/<int:endpoint_id>',
            endpoint='trunk_endpoint_custom',
            resource_class_args=(service, trunk_dao, endpoint_custom_dao),
        )

    def load_iax(self, api):
        service = build_service('iax')

        api.add_resource(
            TrunkEndpointAssociationIAX,
            '/trunks/<int:trunk_id>/endpoints/iax/<int:endpoint_id>',
            endpoint='trunk_endpoint_iax',
            resource_class_args=(service, trunk_dao, endpoint_iax_dao),
        )
