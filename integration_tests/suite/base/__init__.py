# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import contextmanager

from typing import cast
from ..helpers.sysconfd import SysconfdMock
from ..helpers.base import IntegrationTest
from ..helpers.config import TOKEN
from ..helpers.wrappers import IsolatedAction
from ..helpers.helpers import confd as helper_confd, new_client as helper_new_client


class BaseIntegrationTest(IntegrationTest):
    asset = 'base'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_token()
        cls.setup_service_token()
        cls.confd = cls.make_confd()
        cls.wait_strategy.wait(cls)
        cls.setup_provd()
        cls.setup_database()
        cls.setup_helpers()

    @classmethod
    def make_confd(cls):
        return cls.create_confd({'X-Auth-Token': TOKEN})

    @classmethod
    def restart_confd(cls):
        super().restart_confd()
        cls.setup_helpers()
        cls.confd = cls.make_confd()

    @classmethod
    @contextmanager
    def confd_with_config(cls, config):
        with super().confd_with_config(config):
            yield
        cls.wait_strategy.wait(cls)


def setup_module(module):
    BaseIntegrationTest.setUpClass()


def teardown_module(module):
    BaseIntegrationTest.tearDownClass()


class mocks:
    @classmethod
    class provd(IsolatedAction):
        actions = {'generate': BaseIntegrationTest.setup_provd}

    @classmethod
    class sysconfd(IsolatedAction):
        actions = {'generate': BaseIntegrationTest.setup_sysconfd}


class SingletonProxy:
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

    def _reset(self):
        self.obj = None


confd = SingletonProxy(BaseIntegrationTest.create_confd)
confd_csv = SingletonProxy(
    BaseIntegrationTest.create_confd,
    {'Accept': 'text/csv; charset=utf-8', 'X-Auth-Token': TOKEN},
)
create_confd = BaseIntegrationTest.create_confd
auth = SingletonProxy(BaseIntegrationTest.create_auth)
ari = SingletonProxy(BaseIntegrationTest.create_ari)
provd = SingletonProxy(BaseIntegrationTest.create_provd)
db = SingletonProxy(BaseIntegrationTest.create_database)
rabbitmq = SingletonProxy(BaseIntegrationTest.create_bus)
sysconfd: SysconfdMock = cast(
    SysconfdMock, SingletonProxy(BaseIntegrationTest.create_sysconfd)
)

wazo_sound = SingletonProxy(
    BaseIntegrationTest.create_tenant_filesystem, '/var/lib/wazo/sounds'
)
asterisk_sound = SingletonProxy(
    BaseIntegrationTest.create_filesystem, '/usr/share/asterisk/sounds'
)

asterisk_json_doc = SingletonProxy(
    BaseIntegrationTest.create_filesystem,
    '/usr/share/doc/asterisk-doc/json',
)


def reset_confd_clients():
    helper_confd._reset()
    helper_new_client._reset()
    confd._reset()
    confd_csv._reset()


@contextmanager
def confd_with_config(config):
    with BaseIntegrationTest.confd_with_config(config):
        reset_confd_clients()
        yield
    reset_confd_clients()
