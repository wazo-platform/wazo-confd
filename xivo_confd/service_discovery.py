# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

import requests

from xivo_confd.config import API_VERSION


# this function is not executed from the main thread
def self_check(config):
    http_enabled = config['rest_api']['http']['enabled']
    scheme = 'http' if http_enabled else 'https'
    port = config['rest_api'][scheme]['port']
    url = '{}://{}:{}/{}/infos'.format(scheme, 'localhost', port, API_VERSION)

    try:
        return requests.get(url).status_code == 200
    except Exception:
        return False
