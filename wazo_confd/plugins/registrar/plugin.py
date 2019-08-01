# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from .builder import build_dao, build_service
from .resource import RegistrarList, RegistrarItem


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        registrar_dao = build_dao(provd_client)
        service = build_service(registrar_dao, provd_client)

        api.add_resource(
            RegistrarList,
            '/registrars',
            endpoint='registrars',
            resource_class_args=(service,)
        )

        api.add_resource(
            RegistrarItem,
            '/registrars/<id>',
            resource_class_args=(service,)
        )
