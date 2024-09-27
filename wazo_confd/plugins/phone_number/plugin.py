# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import PhoneNumberItem, PhoneNumberList


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']

        api.add_resource(
            PhoneNumberList,
            '/phone-numbers',
        )
        api.add_resource(
            PhoneNumberItem,
            '/phone-numbers/<uuid:uuid>',
        )
