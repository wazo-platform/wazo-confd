# Copyright 2015-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import contextlib
import logging
import signal
import sys
import threading
from functools import partial

import xivo_dao
from wazo_auth_client import Client as AuthClient
from xivo import plugin_helpers
from xivo.consul_helpers import ServiceCatalogRegistration
from xivo.status import StatusAggregator, TokenStatus
from xivo.token_renewer import TokenRenewer

from wazo_confd.helpers.asterisk import PJSIPDoc
from wazo_confd.helpers.middleware import MiddleWareHandle

from . import auth
from ._bus import BusConsumer, BusPublisher, NoopConsumer
from .http_server import HTTPServer, api, app
from .service_discovery import self_check

logger = logging.getLogger(__name__)

MISCONFIGURATION_EXIT_CODE = 78


class Controller:
    def __init__(self, config):
        self.config = config
        self._http_worker = config.get('http_worker', False)
        self._stopping_thread = None
        self._bus_consumer = self._build_bus_consumer()
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

    def _build_bus_consumer(self):
        consumer_class = NoopConsumer if self._http_worker else BusConsumer
        return consumer_class.from_config(self.config['bus'])

    def run(self):
        if self._http_worker and not self.config['rest_api']['reuse_port']:
            logger.error(
                'Cannot start as an HTTP worker: rest_api.reuse_port must be '
                'enabled so the worker can share the listen port with the main '
                'wazo-confd process'
            )
            sys.exit(MISCONFIGURATION_EXIT_CODE)

        xivo_dao.init_db_from_config(self.config)
        signal.signal(signal.SIGTERM, partial(_signal_handler, self))
        signal.signal(signal.SIGINT, partial(_signal_handler, self))

        if self._http_worker:
            service_discovery = contextlib.nullcontext()
        else:
            service_discovery = ServiceCatalogRegistration(
                *self._service_discovery_args
            )

        try:
            with self.token_renewer:
                with self._bus_consumer:
                    with service_discovery:
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
