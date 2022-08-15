# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.extension import dao as extension_dao

from wazo_confd.plugins.extension.service import (
    build_service as build_extension_service,
)

from .resource import LineExtensionItem, LineExtensionList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']
        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        service = build_service()
        extension_service = build_extension_service(provd_client)
        class_args = (service, line_dao, extension_dao)

        api.add_resource(
            LineExtensionItem,
            '/lines/<int:line_id>/extensions/<int:extension_id>',
            endpoint='line_extensions',
            resource_class_args=class_args,
        )
        api.add_resource(
            LineExtensionList,
            '/lines/<int:line_id>/extensions',
            resource_class_args=(service, extension_service, line_dao),
        )
