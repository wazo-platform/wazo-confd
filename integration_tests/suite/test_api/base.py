# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import os

from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase
from xivo_test_helpers.confd.database import DbHelper
from xivo_test_helpers.confd.provd import create_helper as provd_create_helper
from xivo_test_helpers.confd.sysconfd import SysconfdMock
from xivo_test_helpers.confd.client import ConfdClient
from xivo_test_helpers.confd.helpers import device
from xivo_test_helpers.confd.helpers import setup_confd as setup_confd_helpers
from xivo_test_helpers.confd.helpers import setup_new_client as setup_new_client_helpers
from xivo_test_helpers.confd.helpers import setup_database as setup_database_helpers


class IntegrationTest(AssetLaunchingTestCase):
    service = 'confd'
    assets_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets'))

    @classmethod
    def setUpClass(cls):
        super(IntegrationTest, cls).setUpClass()
        cls.setup_helpers()

    @classmethod
    def setup_provd(cls, *args, **kwargs):  # args seems needed for IsolatedAction
        helper = cls.create_provd()
        helper.reset()
        device.provd = helper
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
        db_user = 'asterisk'
        db_password = 'proformatique'
        host = 'localhost'
        port = cls.service_port(5432, 'postgres')
        db = 'asterisk'
        helper = DbHelper.build(db_user, db_password, host, port, db)
        return helper

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
        client = cls.new_client()
        setup_confd_helpers(client)
        setup_new_client_helpers(host='localhost',
                                 port=cls.service_port('9486', 'confd'),
                                 username='admin',
                                 password='proformatique')
        setup_database_helpers(cls.create_database())

    @classmethod
    def create_confd(cls, headers=None, encoder=None):
        client = cls.new_client(headers, encoder)
        return client.url

    @classmethod
    def new_client(cls, headers=None, encoder=None):
        client = ConfdClient.from_options(host='localhost',
                                          port=cls.service_port('9486', 'confd'),
                                          username='admin',
                                          password='proformatique',
                                          headers=headers,
                                          encoder=encoder)
        return client
