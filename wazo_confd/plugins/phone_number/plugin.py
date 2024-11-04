# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.types import PluginDependencies
from .resource import (
    PhoneNumberItem,
    PhoneNumberList,
    PhoneNumberMain,
    PhoneNumberRange,
)
from .service import build_service


class PhoneNumberPluginDependencies(PluginDependencies):
    pass


class Plugin:
    def load(self, dependencies: PhoneNumberPluginDependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            PhoneNumberList,
            '/phone-numbers',
            resource_class_args=(service,),
        )
        api.add_resource(
            PhoneNumberRange,
            '/phone-numbers/ranges',
            resource_class_args=(service,),
        )
        api.add_resource(
            PhoneNumberMain,
            '/phone-numbers/main',
            resource_class_args=(service,),
        )
        api.add_resource(
            PhoneNumberItem,
            '/phone-numbers/<uuid:uuid>',
            endpoint='phone_numbers',
            resource_class_args=(service,),
        )
