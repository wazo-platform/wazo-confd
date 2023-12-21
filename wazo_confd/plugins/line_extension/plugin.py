# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .middleware import LineExtensionMiddleware
from .resource import LineExtensionItem, LineExtensionList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        middleware_handle = dependencies['middleware_handle']

        service = build_service()
        line_extension_middleware = LineExtensionMiddleware(service, middleware_handle)
        middleware_handle.register('line_extension', line_extension_middleware)

        api.add_resource(
            LineExtensionItem,
            '/lines/<int:line_id>/extensions/<int:extension_id>',
            endpoint='line_extensions',
            resource_class_args=(line_extension_middleware,),
        )
        api.add_resource(
            LineExtensionList,
            '/lines/<int:line_id>/extensions',
            resource_class_args=(line_extension_middleware,),
        )
