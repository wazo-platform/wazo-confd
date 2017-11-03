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

from test_api.base import IntegrationTest
from xivo_test_helpers.confd import SingletonProxy
from xivo_test_helpers.confd.wrappers import IsolatedAction


class BaseIntegrationTest(IntegrationTest):
    asset = 'base'

    @classmethod
    def setUpClass(cls):
        super(IntegrationTest, cls).setUpClass()
        cls.setup_provd()
        cls.setup_database()


def setUpModule():
    BaseIntegrationTest.setUpClass()


def tearDownModule():
    BaseIntegrationTest.tearDownClass()


class mocks(object):
    @classmethod
    class provd(IsolatedAction):

        actions = {'generate': BaseIntegrationTest.setup_provd}

    @classmethod
    class sysconfd(IsolatedAction):

        actions = {'generate': BaseIntegrationTest.setup_sysconfd}


confd = SingletonProxy(BaseIntegrationTest.create_confd)
confd_csv = SingletonProxy(BaseIntegrationTest.create_confd, {'Accept': 'text/csv; charset=utf-8'})
provd = SingletonProxy(BaseIntegrationTest.create_provd)
db = SingletonProxy(BaseIntegrationTest.create_database)
