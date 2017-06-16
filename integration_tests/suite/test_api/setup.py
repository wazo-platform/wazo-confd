# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2017 Avencall
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
import subprocess
import logging

logger = logging.getLogger(__name__)

ASSETS_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
ASSET_PATH = os.path.join(ASSETS_ROOT, 'base')


def setup_docker():
    cleanup_docker()
    start_docker()


def stop_docker():
    os.chdir(ASSET_PATH)
    run_cmd(('docker-compose', 'kill'))


def cleanup_docker():
    os.chdir(ASSET_PATH)
    run_cmd(('docker-compose', 'kill'))
    run_cmd(('docker-compose', 'rm', '-f'))


def start_docker():
    os.chdir(ASSET_PATH)
    run_cmd(('docker-compose', 'run', '--rm', '--service-ports', 'tests'))


def run_cmd(cmd):
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    out, _ = process.communicate()
    logger.info(out)
    return out
