# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_auth_client import Client as AuthClient
from xivo_dird_client import Client as DirdClient

from xivo_confd import api
from xivo_dao.resources.infos import dao as infos_dao

from .resource import WizardResource, WizardDiscoverResource
from .service import build_service

logger = logging.getLogger(__name__)


class Plugin(object):

    def load(self, core):
        service_id = core.config['wizard']['service_id']
        service_key = core.config['wizard']['service_key']
        if not service_id or not service_key:
            logger.info('failed to load the wizard plugin: missing service_id or service_key')
            return

        auth_client = AuthClient(username=service_id,
                                 password=service_key,
                                 **core.config['auth'])
        dird_client = DirdClient(**core.config['dird'])
        provd_client = core.provd_client()

        service = build_service(provd_client, auth_client, dird_client, infos_dao)

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
