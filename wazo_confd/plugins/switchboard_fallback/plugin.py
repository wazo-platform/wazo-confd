# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.switchboard import dao as switchboard_dao

from .resource import SwitchboardFallbackList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            SwitchboardFallbackList,
            '/switchboards/<uuid:switchboard_uuid>/fallbacks',
            resource_class_args=(service, switchboard_dao),
        )
