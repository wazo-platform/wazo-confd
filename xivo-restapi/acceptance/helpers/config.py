# -*- coding: UTF-8 -*-
# Copyright (C) 2013  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

import os

from ConfigParser import ConfigParser

CONFIG_FILE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "config.ini"
    )
)


def get_config_value(section, key):
    local_config = '%s.local' % CONFIG_FILE_PATH
    if os.path.exists(local_config):
        config_file = local_config
    else:
        config_file = CONFIG_FILE_PATH

    if not os.path.exists(config_file):
        raise Exception("config file not found (%s)" % config_file)

    parser = ConfigParser()
    parser.read(config_file)
    return parser.get(section, key)
