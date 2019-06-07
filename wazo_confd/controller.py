# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import signal

from functools import partial

import xivo_dao

from wazo_auth_client import Client as AuthClient
from xivo import plugin_helpers
from xivo.consul_helpers import ServiceCatalogRegistration
from xivo.token_renewer import TokenRenewer

from .http_server import api, HTTPServer
from .service_discovery import self_check

logger = logging.getLogger(__name__)


class Controller:

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

        auth_client = AuthClient(**config['auth'])
        self.token_renewer = TokenRenewer(auth_client)

        self.http_server = HTTPServer(config)

        plugin_helpers.load(
            namespace='wazo_confd.plugins',
            names=config['enabled_plugins'],
            dependencies={
                'api': api,
                'config': config,
                'token_changed_subscribe': self.token_renewer.subscribe_to_token_change,
            }
        )

    def run(self):
        logger.info('xivo-confd running...')
        xivo_dao.init_db_from_config(self.config)
        signal.signal(signal.SIGTERM, partial(_sigterm_handler, self))

        with self.token_renewer:
            with ServiceCatalogRegistration(*self._service_discovery_args):
                self.http_server.run()

    def stop(self, reason):
        logger.warning('Stopping xivo-confd: %s', reason)
        self.http_server.stop()


def _sigterm_handler(controller, signum, frame):
    controller.stop(reason='SIGTERM')
