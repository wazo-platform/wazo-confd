# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.tenant import dao as tenant_dao

from .resource import CallFilterItem, CallFilterList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            CallFilterList, '/callfilters', resource_class_args=(tenant_dao, service)
        )

        api.add_resource(
            CallFilterItem,
            '/callfilters/<int:id>',
            endpoint='callfilters',
            resource_class_args=(service,),
        )
