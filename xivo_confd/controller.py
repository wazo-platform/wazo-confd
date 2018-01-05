# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging
import xivo_dao

from functools import partial

from xivo import plugin_helpers
from xivo.consul_helpers import ServiceCatalogRegistration

from .authentication.confd_auth import auth
from .http_server import api, HTTPServer
from .service_discovery import self_check

logger = logging.getLogger(__name__)


class Controller(object):

    def __init__(self, config):
        self.config = config
        self._service_discovery_args = [
            'xivo-confd',
            config['uuid'],
            config['consul'],
            config['service_discovery'],
            config['bus'],
            partial(self_check, config),
        ]

        auth.set_config(config)
        self.http_server = HTTPServer(config)
        plugin_helpers.load(
            namespace='xivo_confd.plugins',
            names=config['enabled_plugins'],
            dependencies={
                'api': api,
                'config': config,
            }
        )

    def run(self):
        logger.info('xivo-confd running...')
        xivo_dao.init_db_from_config(self.config)
        with ServiceCatalogRegistration(*self._service_discovery_args):
            self.http_server.run()
