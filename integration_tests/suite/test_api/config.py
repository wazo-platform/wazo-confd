# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

CONTEXT = 'default'
INCALL_CONTEXT = 'from-extern'
EXTENSION_RANGE = range(1000, 5001)


def confd_host():
    return os.environ.get('HOST', 'localhost')


def confd_port():
    return int(os.environ.get('PORT', 9486))


def confd_https():
    return os.environ.get('HTTPS', '1') == '1'


def confd_base_url(host=None, port=None, https=None):
    if host is None:
        host = confd_host()
    if port is None:
        port = confd_port()
    if https is None:
        https = confd_https()
    scheme = 'https' if https else 'http'
    return '{}://{}:{}/1.1'.format(scheme, host, port)
