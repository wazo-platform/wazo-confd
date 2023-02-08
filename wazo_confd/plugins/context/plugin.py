# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from .middleware import ContextMiddleWare
from .resource import ContextItem, ContextList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        middleware_handle = dependencies['middleware_handle']

        service = build_service()
        context_middleware = ContextMiddleWare(service)
        middleware_handle.register('context', context_middleware)

        api.add_resource(ContextList, '/contexts', resource_class_args=(service,))

        api.add_resource(
            ContextItem,
            '/contexts/<int:id>',
            endpoint='contexts',
            resource_class_args=(service, context_middleware),
        )
