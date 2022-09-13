# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from wazo_test_helpers import until
from wazo_test_helpers.hamcrest.raises import raises
from requests.exceptions import ConnectionError
from ..helpers.helpers import confd as helper_confd, new_client as helper_new_client
from . import auth, BaseIntegrationTest, confd, confd_csv

from hamcrest import (
    assert_that,
    calling,
    has_entries,
)

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

    response = confd.status.get()
    assert_that(response.item, has_entries(**expected_status_ok_entries))


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
    rabbitmq = BaseIntegrationTest.create_bus()
    until.true(rabbitmq.is_up, tries=5)

    def _bus_consumer_status_is_ok():
        response = confd.status.get()
        response.assert_status(200)
        assert_that(response.item, has_entries(**expected_status_ok_entries))

    until.assert_(_bus_consumer_status_is_ok, tries=10)


def test_confd_status_fails_when_wazo_auth_is_down():
    BaseIntegrationTest.stop_service('confd')
    BaseIntegrationTest.stop_service('auth')
    BaseIntegrationTest.start_service('confd')
    BaseIntegrationTest.setup_helpers()
    helper_confd._reset()
    helper_new_client._reset()
    confd._reset()
    confd_csv._reset()

    def _raises_ConnectionError():
        assert_that(
            calling(confd.status.get),
            raises(ConnectionError),
        )

    until.assert_(_raises_ConnectionError, tries=10)

    BaseIntegrationTest.start_service('auth')
    auth._reset()
    until.true(auth.is_up, tries=5)
    BaseIntegrationTest.setup_token()

    def _not_raise_ConnectionError():
        response = confd.status.get()
        response.assert_status(200)
        assert_that(response.item, has_entries(**expected_status_ok_entries))

    until.assert_(_not_raise_ConnectionError, tries=10)
