# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import PhoneNumberItem, PhoneNumberList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            PhoneNumberList,
            '/phone-numbers',
            resource_class_args=(service,),
        )
        api.add_resource(
            PhoneNumberItem,
            '/phone-numbers/<uuid:uuid>',
            endpoint='phone_numbers',
            resource_class_args=(service,),
        )
