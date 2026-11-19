# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import threading
from unittest.mock import MagicMock, patch

import pytest

from ..config import DEFAULT_CONFIG
from ..controller import Controller


@pytest.fixture
def components():
    with (
        patch('wazo_confd.controller.BusConsumer') as bus_consumer_class,
        patch('wazo_confd.controller.BusPublisher'),
        patch('wazo_confd.controller.HTTPServer') as http_server_class,
        patch('wazo_confd.controller.AuthClient'),
        patch('wazo_confd.controller.TokenRenewer') as token_renewer_class,
        patch('wazo_confd.controller.PJSIPDoc'),
        patch('wazo_confd.controller.plugin_helpers'),
        patch('wazo_confd.controller.xivo_dao'),
        patch('wazo_confd.controller.signal'),
        patch('wazo_confd.controller.ServiceCatalogRegistration') as registration,
        patch('wazo_confd.controller.app') as app,
        patch('wazo_confd.controller.auth'),
    ):
        app.config = {'auth': {}}
        bus_consumer_class.from_config.return_value = MagicMock()
        http_server = http_server_class.return_value
        serving = threading.Event()
        stopping = threading.Event()

        def serve_until_stopped():
            serving.set()
            stopping.wait()

        http_server.run.side_effect = serve_until_stopped
        http_server.stop.side_effect = stopping.set
        yield {
            'bus_consumer': bus_consumer_class.from_config.return_value,
            'http_server': http_server,
            'serving': serving,
            'token_renewer': token_renewer_class.return_value,
            'registration': registration,
        }
        stopping.set()


def make_controller():
    config = dict(DEFAULT_CONFIG, uuid='00000000-0000-4000-8000-000000000001')
    return Controller(config)


def test_run_serves_with_every_component_until_stopped(components):
    controller = make_controller()
    running = threading.Thread(target=controller.run)

    running.start()
    assert components['serving'].wait(timeout=5)

    components['token_renewer'].__enter__.assert_called_once()
    components['bus_consumer'].__enter__.assert_called_once()
    components['registration'].return_value.__enter__.assert_called_once()
    assert running.is_alive()

    controller.stop(reason='test')
    running.join(timeout=5)

    assert not running.is_alive()
    components['registration'].return_value.__exit__.assert_called_once()
    components['bus_consumer'].__exit__.assert_called_once()
    components['token_renewer'].__exit__.assert_called_once()


def test_status_reports_the_bus_consumer(components):
    controller = make_controller()

    controller.status_aggregator.status()

    components['bus_consumer'].provide_status.assert_called_once()
