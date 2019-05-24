# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import ApplicationItem, ApplicationList
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            ApplicationList,
            '/applications',
            resource_class_args=(service,)
        )

        api.add_resource(
            ApplicationItem,
            '/applications/<uuid:application_uuid>',
            endpoint='applications',
            resource_class_args=(service,)
        )
