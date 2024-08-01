# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import LocalizationResource
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']

        service = build_service()

        api.add_resource(
            LocalizationResource, '/localization', resource_class_args=(service,)
        )
