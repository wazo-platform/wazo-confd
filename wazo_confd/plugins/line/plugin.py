# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.extension import dao as extension_dao

from wazo_confd.plugins.line_extension.service import (
    build_service as build_line_extension_service,
)

from .resource import LineItem, LineList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        service = build_service(provd_client)
        line_extension_service = build_line_extension_service()

        api.add_resource(
            LineItem,
            '/lines/<int:id>',
            endpoint='lines',
            resource_class_args=(
                service,
                line_extension_service,
                line_dao,
                extension_dao,
            ),
        )
        api.add_resource(LineList, '/lines', resource_class_args=(service,))
