# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2016 Avencall
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
from provd import create_helper as create_provd_helper


class SingletonProxy(object):

    def __init__(self, func):
        self.func = func
        self.obj = None

    def __getattr__(self, name):
        if self.obj is None:
            self.obj = self.func()
        return getattr(self.obj, name)

    def __call__(self, *args, **kwargs):
        if self.obj is None:
            self.obj = self.func()
        return self.obj(*args, **kwargs)


def setup():
    if os.environ.get('DOCKER', '1') == '1':
        setup_docker()
    setup_provd()
    setup_database()


def teardown():
    if os.environ.get('DOCKER', '1') == '1':
        stop_docker()


confd = SingletonProxy(new_confd)
client = SingletonProxy(new_client)
provd = SingletonProxy(create_provd_helper)
