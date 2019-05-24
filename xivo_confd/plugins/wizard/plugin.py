# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from wazo_auth_client import Client as AuthClient
from wazo_provd_client import Client as ProvdClient

from xivo_dao.resources.infos import dao as infos_dao

from .resource import WizardResource, WizardDiscoverResource
from .service import build_service

logger = logging.getLogger(__name__)


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        service_id = config['wizard']['service_id']
        service_key = config['wizard']['service_key']
        auth_config = dict(config['auth'])
        auth_config.pop('username', None)
        auth_config.pop('password', None)
        if not service_id or not service_key:
            logger.info('failed to load the wizard plugin: missing service_id or service_key')
            return

        auth_client = AuthClient(username=service_id,
                                 password=service_key,
                                 **auth_config)
        provd_client = ProvdClient(**config['provd'])

        service = build_service(provd_client, auth_client, infos_dao)

        api.add_resource(
            WizardResource,
            '/wizard',
            endpoint='wizard',
            resource_class_args=(service,)
        )

        api.add_resource(
            WizardDiscoverResource,
            '/wizard/discover',
            resource_class_args=(service,)
        )
