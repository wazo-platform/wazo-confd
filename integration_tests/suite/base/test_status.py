# Copyright 2022-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries
from wazo_test_helpers import until

from ..helpers.bus import BusClient as bus_client
from ..helpers.bus import setup_bus
from . import BaseIntegrationTest, auth, confd, rabbitmq, reset_confd_clients

expected_status_ok_entries = {
    'bus_consumer': {
        'status': 'ok',
    },
    'master_tenant': {
        'status': 'ok',
    },
    'rest_api': {
        'status': 'ok',
    },
    'service_token': {
        'status': 'ok',
    },
}


def test_confd_status_is_all_ok():
    def _bus_is_up():
        response = confd.status.get()
        assert_that(response.item, has_entries(**expected_status_ok_entries))

    until.assert_(_bus_is_up, tries=10)


def test_confd_status_fails_when_rabbitmq_is_down():
    expected_bus_status_fail_entries = {
        'bus_consumer': {
            'status': 'fail',
        },
        'master_tenant': {
            'status': 'ok',
        },
        'rest_api': {
            'status': 'ok',
        },
        'service_token': {
            'status': 'ok',
        },
    }
    BaseIntegrationTest.stop_service('rabbitmq')
    response = confd.status.get()
    assert_that(response.item, has_entries(**expected_bus_status_fail_entries))

    BaseIntegrationTest.start_service('rabbitmq')
    until.true(rabbitmq.is_up, tries=10)
    setup_bus(host='127.0.0.1', port=BaseIntegrationTest.service_port(5672, 'rabbitmq'))
    bus_client._reset_bus()
    bus_client._bus = bus_client._create_client()
    until.true(bus_client._bus.is_up, tries=5)

    def _bus_consumer_status_is_ok():
        response = confd.status.get()
        response.assert_status(200)
        assert_that(response.item, has_entries(**expected_status_ok_entries))

    until.assert_(_bus_consumer_status_is_ok, tries=10)


def test_confd_status_fails_when_wazo_auth_is_down():
    expected_status_fail_entries = {
        'bus_consumer': {
            'status': 'ok',
        },
        'master_tenant': {
            'status': 'fail',
        },
        'rest_api': {
            'status': 'ok',
        },
        'service_token': {
            'status': 'fail',
        },
    }
    BaseIntegrationTest.restart_confd()
    reset_confd_clients()

    BaseIntegrationTest.restart_service('auth')
    auth._reset()
    until.true(auth.is_up, tries=10)
    BaseIntegrationTest.setup_token()

    response = until.return_(confd.status.get, timeout=5)
    assert_that(response.item, has_entries(**expected_status_fail_entries))

    BaseIntegrationTest.setup_service_token()

    def _status_is_all_ok():
        response = confd.status.get()
        response.assert_status(200)
        assert_that(response.item, has_entries(**expected_status_ok_entries))

    until.assert_(_status_is_all_ok, tries=30)
