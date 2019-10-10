# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.queue import dao as queue_dao
from xivo_dao.resources.extension import dao as extension_dao

from .resource import QueueExtensionItem
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            QueueExtensionItem,
            '/queues/<int:queue_id>/extensions/<int:extension_id>',
            endpoint='queue_extensions',
            resource_class_args=(service, queue_dao, extension_dao),
        )
