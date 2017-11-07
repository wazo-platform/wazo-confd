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

from ..test_api.base import IntegrationTest
from xivo_test_helpers.confd.wrappers import IsolatedAction


class BaseIntegrationTest(IntegrationTest):
    asset = 'base'

    @classmethod
    def setUpClass(cls):
        super(IntegrationTest, cls).setUpClass()
        cls.setup_provd()
        cls.setup_database()
        cls.setup_helpers()


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


class SingletonProxy(object):

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.func_args = args
        self.func_kwargs = kwargs
        self.obj = None

    def __getattr__(self, name):
        if self.obj is None:
            self.obj = self.func(*self.func_args, **self.func_kwargs)
        return getattr(self.obj, name)

    def __call__(self, *args, **kwargs):
        if self.obj is None:
            self.obj = self.func(*self.func_args, **self.func_kwargs)
        return self.obj(*args, **kwargs)


confd = SingletonProxy(BaseIntegrationTest.create_confd)
confd_csv = SingletonProxy(BaseIntegrationTest.create_confd, {'Accept': 'text/csv; charset=utf-8',
                                                              'X-Auth-Token': 'valid-token'})
provd = SingletonProxy(BaseIntegrationTest.create_provd)
db = SingletonProxy(BaseIntegrationTest.create_database)
