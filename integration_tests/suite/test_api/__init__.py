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
import logging
import subprocess
import time

from client import ConfdClient

ASSETS_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
ASSET_PATH = os.path.join(ASSETS_ROOT, 'base')
DOCKER_SERVICES = ('testdeps', 'tests')

logger = logging.getLogger(__name__)


class BuilderProxy(object):

    def __init__(self, func):
        self.func = func

    def __getattr__(self, name):
        return getattr(self.func(), name)

    def __call__(self):
        return self.func()


def setup():
    setup_docker()


def teardown():
    stop_docker()


def new_client(headers=None):
    xivo_host = os.environ.get('XIVO_HOST', 'localhost')
    xivo_confd_port = os.environ.get('XIVO_CONFD_PORT', 9486)
    xivo_confd_login = os.environ.get('XIVO_CONFD_LOGIN', 'admin')
    xivo_confd_password = os.environ.get('XIVO_CONFD_PASSWORD', 'proformatique')
    xivo_https = bool(os.environ.get('XIVO_HTTPS', ''))
    client = ConfdClient.from_options(host=xivo_host,
                                      port=xivo_confd_port,
                                      username=xivo_confd_login,
                                      password=xivo_confd_password,
                                      https=xivo_https,
                                      headers=headers)
    return client


def new_confd(headers=None):
    return new_client(headers).url


def setup_docker():
    _cleanup_docker()
    _start_docker()


def stop_docker():
    os.chdir(ASSET_PATH)
    _run_cmd(('docker-compose', 'kill'))


def _cleanup_docker():
    os.chdir(ASSET_PATH)
    _run_cmd(('docker-compose', 'kill'))
    _run_cmd(('docker-compose', 'rm', '-f'))


def _start_docker():
    os.chdir(ASSET_PATH)
    for service in DOCKER_SERVICES:
        cmd = ('docker-compose', 'run', '--rm', '--service-ports', service)
        _run_cmd(cmd)
        time.sleep(3)


def _run_cmd(cmd):
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    out, _ = process.communicate()
    logger.info(out)
    return out


confd = BuilderProxy(new_confd)
client = BuilderProxy(new_client)
