# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.outcall import dao as outcall_dao
from xivo_dao.resources.extension import dao as extension_dao

from .resource import OutcallExtensionItem
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            OutcallExtensionItem,
            '/outcalls/<int:outcall_id>/extensions/<int:extension_id>',
            endpoint='outcall_extensions',
            resource_class_args=(service, outcall_dao, extension_dao)
        )
