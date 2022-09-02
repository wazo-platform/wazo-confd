# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import SwaggerResource


class Plugin:
    def load(self, dependencies):
        api_v1_1 = dependencies['api_v1_1']
        api_v2_0 = dependencies['api_v2_0']

        api_v1_1.add_resource(
            SwaggerResource,
            '/api/api.yml',
            endpoint='api_v1_1',
            resource_class_args=('api.yml',),
        )
        api_v2_0.add_resource(
            SwaggerResource,
            '/api/api.yml',
            endpoint='api_v2_0',
            resource_class_args=('api_v2_0.yml',),
        )
