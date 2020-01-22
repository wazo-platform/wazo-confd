# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from wazo_confd import bus, sysconfd
from wazo_confd.plugins.sip_general.service import build_service as build_sip_general_service
from wazo_confd.plugins.registrar import builder as registrar_builder

from .notifier import HANotifier
from .resource import HAResource
from .service import HAService


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        sip_general_service = build_sip_general_service()

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)
        registrar_dao = registrar_builder.build_dao(provd_client)
        registrar_service = registrar_builder.build_service(registrar_dao, provd_client)

        notifier = HANotifier(bus, sysconfd)
        service = HAService(sip_general_service, registrar_service, notifier, sysconfd)

        api.add_resource(HAResource, '/ha', resource_class_args=(service,))
