# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .ari import Client as ARIClient
from .resource import SoundLanguageList
from .service import build_service, build_ari_client_proxy


class Plugin(object):

    def load(self, core):
        api = core.api
        bus = None  # TODO build_bus_consumer
        ari_client = ARIClient(**core.config['ari'])
        ari_client_proxy = build_ari_client_proxy(ari_client, bus)
        service = build_service(ari_client_proxy)

        api.add_resource(
            SoundLanguageList,
            '/sounds/languages',
            resource_class_args=(service,)
        )
