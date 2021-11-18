# Copyright 2015-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import signal

from functools import partial

import xivo_dao

from wazo_auth_client import Client as AuthClient
from xivo import plugin_helpers
from xivo.consul_helpers import ServiceCatalogRegistration
from xivo.token_renewer import TokenRenewer

from wazo_confd.helpers.asterisk import PJSIPDoc

from . import auth
from ._bus import BusConsumer, bus_consumer_thread
from .http_server import api, app, HTTPServer
from .service_discovery import self_check

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, config):
        self.config = config
        self._bus_consumer = BusConsumer(config['bus'])
        self._service_discovery_args = [
            'wazo-confd',
            config['uuid'],
            config['consul'],
            config['service_discovery'],
            config['bus'],
            partial(self_check, config),
        ]
        self.http_server = HTTPServer(config)
        auth_client = AuthClient(**config['auth'])
        self.token_renewer = TokenRenewer(auth_client)
        if not app.config['auth'].get('master_tenant_uuid'):
            self.token_renewer.subscribe_to_next_token_details_change(
                auth.init_master_tenant
            )
        pjsip_doc = PJSIPDoc(config['pjsip_config_doc_filename'])

        plugin_helpers.load(
            namespace='wazo_confd.plugins',
            names=config['enabled_plugins'],
            dependencies={
                'api': api,
                'config': config,
                'token_changed_subscribe': self.token_renewer.subscribe_to_token_change,
                'bus_consumer': self._bus_consumer,
                'auth_client': auth_client,
                'pjsip_doc': pjsip_doc,
            },
        )

    def run(self):
        logger.info('wazo-confd starting...')
        xivo_dao.init_db_from_config(self.config)
        signal.signal(signal.SIGTERM, partial(_sigterm_handler, self))

        with self.token_renewer:
            with ServiceCatalogRegistration(*self._service_discovery_args):
                with bus_consumer_thread(self._bus_consumer):
                    self.http_server.run()

    def stop(self, reason):
        logger.warning('Stopping wazo-confd: %s', reason)
        self.http_server.stop()


def _sigterm_handler(controller, signum, frame):
    controller.stop(reason='SIGTERM')
