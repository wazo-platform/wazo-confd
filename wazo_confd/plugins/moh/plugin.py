# Copyright 2017-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.tenant import dao as tenant_dao

from .resource import MohItem, MohList, MohFileItem
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(MohList, '/moh', resource_class_args=(tenant_dao, service))

        api.add_resource(
            MohItem, '/moh/<uuid>', endpoint='moh', resource_class_args=(service,)
        )

        api.add_resource(
            MohFileItem,
            '/moh/<uuid>/files/<filename:filename>',
            endpoint='mohfileitem',
            resource_class_args=(service,),
        )
