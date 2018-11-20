# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os

from xivo_auth_client import Client as AuthClient
from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase
from xivo_test_helpers.bus import BusClient

from .ari import ARIClient
from .bus import setup_bus as setup_bus_helpers
from .client import ConfdClient
from .database import create_helper as db_create_helper
from .filesystem import FileSystemClient
from .helpers import setup_confd as setup_confd_helpers
from .helpers import setup_database as setup_database_helpers
from .helpers import setup_new_client as setup_new_client_helpers
from .helpers import setup_provd as setup_provd_helpers
from .provd import create_helper as provd_create_helper
from .sysconfd import SysconfdMock


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

    @classmethod
    def create_auth(cls):
        return AuthClient(host='localhost', port=cls.service_port(9497, 'auth'), verify_certificate=False)

    @classmethod
    def create_ari(cls):
        return ARIClient(host='localhost', port=cls.service_port(5039, 'ari'))

    @classmethod
    def create_filesystem(cls, base_path):
        return FileSystemClient(base_path=base_path, execute=cls.docker_exec)
