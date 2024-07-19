# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import IngressHTTPItem, IngressHTTPList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            IngressHTTPList,
            '/ingresses/http',
            resource_class_args=(service,),
        )

        api.add_resource(
            IngressHTTPItem,
            '/ingresses/http/<uuid:uuid>',
            resource_class_args=(service,),
            endpoint='ingresses_http',
        )
