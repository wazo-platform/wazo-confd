# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.register_iax import dao as register_iax_dao
from xivo_dao.resources.trunk import dao as trunk_dao

from .resource import TrunkRegisterAssociationSIP, TrunkRegisterAssociationIAX
from .service import build_service_iax


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        self.load_iax(api)

    def load_iax(self, api):
        service = build_service_iax()

        api.add_resource(
            TrunkRegisterAssociationIAX,
            '/trunks/<int:trunk_id>/registers/iax/<int:register_id>',
            endpoint='trunk_register_iax',
            resource_class_args=(service, trunk_dao, register_iax_dao),
        )
