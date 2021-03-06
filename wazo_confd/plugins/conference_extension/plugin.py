# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.conference import dao as conference_dao
from xivo_dao.resources.extension import dao as extension_dao

from .resource import ConferenceExtensionItem
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            ConferenceExtensionItem,
            '/conferences/<int:conference_id>/extensions/<int:extension_id>',
            endpoint='conference_extensions',
            resource_class_args=(service, conference_dao, extension_dao),
        )
