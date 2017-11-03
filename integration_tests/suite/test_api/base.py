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
from xivo_test_helpers.confd.setup import setup_database
from xivo_test_helpers.confd.provd import create_helper as provd_create_helper
from xivo_test_helpers.confd.sysconfd import SysconfdMock
from xivo_test_helpers.confd.helpers import device


class IntegrationTest(AssetLaunchingTestCase):
    service = 'confd'
    assets_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets'))

    @classmethod
    def setUpClass(cls):
        super(IntegrationTest, cls).setUpClass()
        cls.setup_provd()
        setup_database()

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
    def setup_sysconfd(cls, *args, **kwargs):  # args seems needed for IsolatedAction
        helper = cls.create_sysconfd()
        helper.clear()
        return helper

    @classmethod
    def create_sysconfd(cls):
        url = 'http://localhost:{port}'.format(port=cls.service_port(8668, 'sysconfd'))
        return SysconfdMock(url)
