# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.extension import dao as extension_dao

from .resource import IncallExtensionItem
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            IncallExtensionItem,
            '/incalls/<int:incall_id>/extensions/<int:extension_id>',
            endpoint='incall_extensions',
            resource_class_args=(service, incall_dao, extension_dao)
        )
