# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import signal
import threading

from functools import partial

import xivo_dao

from wazo_auth_client import Client as AuthClient
from wazo import plugin_helpers
from wazo.consul_helpers import ServiceCatalogRegistration
from wazo.status import StatusAggregator, TokenStatus
from wazo.token_renewer import TokenRenewer

from wazo_confd.helpers.asterisk import PJSIPDoc
from wazo_confd.helpers.middleware import MiddleWareHandle

from . import auth
from ._bus import BusPublisher, BusConsumer
from .http_server import api, app, HTTPServer
from .service_discovery import self_check

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, config):
        self.config = config
        self._bus_consumer = BusConsumer.from_config(config['bus'])
        self._bus_publisher = BusPublisher.from_config(config['uuid'], config['bus'])
        self._bus_publisher.set_as_reference()
        self.status_aggregator = StatusAggregator()
        self.token_status = TokenStatus()
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
        middleware_handle = MiddleWareHandle()
        self.token_renewer.subscribe_to_token_change(
            self.token_status.token_change_callback
        )
        self.status_aggregator.add_provider(auth.provide_status)
        self.status_aggregator.add_provider(self.token_status.provide_status)
        self.status_aggregator.add_provider(self._bus_consumer.provide_status)

        plugin_helpers.load(
            namespace='wazo_confd.plugins',
            names=config['enabled_plugins'],
            dependencies={
                'api': api,
                'config': config,
                'token_changed_subscribe': self.token_renewer.subscribe_to_token_change,
                'bus_consumer': self._bus_consumer,
                'bus_publisher': self._bus_publisher,
                'auth_client': auth_client,
                'middleware_handle': middleware_handle,
                'pjsip_doc': pjsip_doc,
                'status_aggregator': self.status_aggregator,
            },
        )

    def run(self):
        logger.info('wazo-confd starting...')
        xivo_dao.init_db_from_config(self.config)
        signal.signal(signal.SIGTERM, partial(_signal_handler, self))
        signal.signal(signal.SIGINT, partial(_signal_handler, self))

        try:
            with self.token_renewer:
                with self._bus_consumer:
                    with ServiceCatalogRegistration(*self._service_discovery_args):
                        self.http_server.run()
        finally:
            if self._stopping_thread:
                self._stopping_thread.join()

    def stop(self, reason):
        logger.warning('Stopping wazo-confd: %s', reason)
        self._stopping_thread = threading.Thread(
            target=self.http_server.stop, name=reason
        )
        self._stopping_thread.start()


def _signal_handler(controller, signum, frame):
    controller.stop(reason=signal.Signals(signum).name)
