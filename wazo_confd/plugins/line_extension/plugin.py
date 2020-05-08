# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.extension import dao as extension_dao

from .resource import LineExtensionItem
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()
        class_args = (service, line_dao, extension_dao)

        api.add_resource(
            LineExtensionItem,
            '/lines/<int:line_id>/extensions/<int:extension_id>',
            endpoint='line_extensions',
            resource_class_args=class_args,
        )
