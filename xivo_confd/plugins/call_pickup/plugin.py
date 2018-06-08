# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import CallPickupItem, CallPickupList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            CallPickupList,
            '/callpickups',
            resource_class_args=(service,)
        )

        api.add_resource(
            CallPickupItem,
            '/callpickups/<int:id>',
            endpoint='callpickups',
            resource_class_args=(service,)
        )
