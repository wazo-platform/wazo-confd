# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2015 Avencall
#
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
from setup import setup_docker, stop_docker, new_client, new_confd, \
    setup_provd, setup_database


class FactoryProxy(object):

    def __init__(self, factory_func):
        self.factory_func = factory_func

    def __getattr__(self, name):
        return getattr(self.factory_func(), name)

    def __call__(self):
        return self.factory_func()


def setup():
    if os.environ.get('DOCKER', '1') == '1':
        setup_docker()
    setup_provd()
    setup_database()


def teardown():
    if os.environ.get('DOCKER', '1') == '1':
        stop_docker()


confd = FactoryProxy(new_confd)
client = FactoryProxy(new_client)
