# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import ExternalNumberItem, ExternalNumberList


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']

        api.add_resource(
            ExternalNumberList,
            '/external/numbers',
        )
        api.add_resource(ExternalNumberItem, '/external/numbers/<uuid:uuid>')
