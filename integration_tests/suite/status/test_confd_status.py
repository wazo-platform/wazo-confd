# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_test_helpers import until
from wazo_test_helpers.hamcrest.raises import raises
from requests.exceptions import ConnectionError

from hamcrest import (
    assert_that,
    calling,
    has_entries,
    has_entry,
)

from ..helpers.base import IntegrationTest as BaseIntegrationTest


class IntegrationTest(BaseIntegrationTest):
    asset = 'base'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_token()
        cls.setup_helpers()
        cls.confd = cls.create_confd()
        cls.provd = cls.create_provd()
        cls.db = cls.create_database()
        cls.bus = cls.create_bus('wazo-headers', 'headers')
        until.true(cls.bus.is_up, timeout=10)


class TestStatusAllOk(IntegrationTest):
    def test_confd_status_all_ok(self):

        response = self.confd.status.get()
        assert_that(
            response.item,
            has_entries(
                bus_consumer=has_entry('status', 'ok'),
                master_tenant=has_entry('status', 'ok'),
                rest_api=has_entry('status', 'ok'),
                service_token=has_entry('status', 'ok'),
            ),
        )


class TestStatusFailWhenRabbitMQisDown(IntegrationTest):
    def test_confd_status_fails_when_rabbitmq_down(self):

        self.stop_service('rabbitmq')
        response = self.confd.status.get()
        assert_that(
            response.item,
            has_entries(
                bus_consumer=has_entry('status', 'fail'),
                master_tenant=has_entry('status', 'ok'),
                rest_api=has_entry('status', 'ok'),
                service_token=has_entry('status', 'ok'),
            ),
        )

        self.setUpClass()
        response = self.confd.status.get()
        assert_that(
            response.item,
            has_entries(
                bus_consumer=has_entry('status', 'ok'),
                master_tenant=has_entry('status', 'ok'),
                rest_api=has_entry('status', 'ok'),
                service_token=has_entry('status', 'ok'),
            ),
        )


class TestStatusFailWhenWazoAuthisDown(IntegrationTest):
    def test_confd_status_fails_when_wazo_auth_is_down(self):

        self.stop_service('confd')
        self.stop_service('auth')
        self.start_service('confd')

        assert_that(
            calling(self.confd.status.get),
            raises(ConnectionError),
        )

        self.setUpClass()
        response = self.confd.status.get()
        response.assert_status(200)
        assert_that(
            response.item,
            has_entries(
                bus_consumer=has_entry('status', 'ok'),
                master_tenant=has_entry('status', 'ok'),
                rest_api=has_entry('status', 'ok'),
                service_token=has_entry('status', 'ok'),
            ),
        )
