# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os

from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase
from xivo_test_helpers.bus import BusClient
from xivo_test_helpers.confd.bus import setup_bus as setup_bus_helpers
from xivo_test_helpers.confd.database import create_helper as db_create_helper
from xivo_test_helpers.confd.provd import create_helper as provd_create_helper
from xivo_test_helpers.confd.sysconfd import SysconfdMock
from xivo_test_helpers.confd.client import ConfdClient
from xivo_test_helpers.confd.helpers import setup_confd as setup_confd_helpers
from xivo_test_helpers.confd.helpers import setup_database as setup_database_helpers
from xivo_test_helpers.confd.helpers import setup_new_client as setup_new_client_helpers
from xivo_test_helpers.confd.helpers import setup_provd as setup_provd_helpers


class IntegrationTest(AssetLaunchingTestCase):
    service = 'confd'
    assets_root = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')

    @classmethod
    def setup_provd(cls, *args, **kwargs):  # args seems needed for IsolatedAction
        helper = cls.create_provd()
        helper.reset()
        return helper

    @classmethod
    def create_provd(cls):
        return provd_create_helper(port=cls.service_port(8666, 'provd'))

    @classmethod
    def setup_database(cls):
        helper = cls.create_database()
        helper.recreate()
        return helper

    @classmethod
    def create_database(cls):
        return db_create_helper(port=cls.service_port(5432, 'postgres'))

    @classmethod
    def setup_sysconfd(cls, *args, **kwargs):  # args seems needed for IsolatedAction
        helper = cls.create_sysconfd()
        helper.clear()
        return helper

    @classmethod
    def create_sysconfd(cls):
        url = 'http://localhost:{port}'.format(port=cls.service_port(8668, 'sysconfd'))
        return SysconfdMock(url)

    @classmethod
    def setup_helpers(cls):
        setup_confd_helpers(host='localhost', port=cls.service_port('9486', 'confd'))
        setup_new_client_helpers(host='localhost', port=cls.service_port('9486', 'confd'))
        setup_database_helpers(host='localhost', port=cls.service_port(5432, 'postgres'))
        setup_provd_helpers(host='localhost', port=cls.service_port(8666, 'provd'))
        setup_bus_helpers(host='localhost', port=cls.service_port(5672, 'rabbitmq'))

    @classmethod
    def create_confd(cls, headers=None, encoder=None):
        client = cls.new_client(headers, encoder)
        return client.url

    @classmethod
    def new_client(cls, headers=None, encoder=None):
        client = ConfdClient.from_options(host='localhost',
                                          port=cls.service_port('9486', 'confd'),
                                          headers=headers,
                                          encoder=encoder)
        return client

    @classmethod
    def create_bus(cls):
        port = cls.service_port(5672, 'rabbitmq')
        client = BusClient.from_connection_fields(host='localhost', port=port)
        return client
