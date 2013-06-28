# -*- coding: UTF-8 -*-
#
# Copyright (C) 2012  Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_restapi.rest import rest_encoder
from acceptance.features.steps.helpers.config import get_config_value
import requests


class WsUtils(object):
    '''
    This helper class is a forerunner of a library
    proposing methods for easy implementation of
    REST web services
    '''

    def __init__(self):
        hostname = get_config_value('xivo', 'hostname')
        protocol = get_config_value('restapi', 'protocol')
        port = get_config_value('restapi', 'port')
        api_version = get_config_value('restapi', 'api_version')

        self.baseurl = "%s://%s:%s/%s" % (protocol, hostname, port, api_version)
        self.username = get_config_value('restapi', 'username')
        self.password = get_config_value('restapi', 'password')

    def rest_get(self, path):
        url = "%s/%s" % (self.baseurl, path)
        response = requests.get(url,
                                verify=False,
                                headers={'Content-Type': 'application/json'},
                                auth=requests.auth.HTTPBasicAuth(self.username, self.password))
        return self._process_response(response)

    def rest_post(self, path, payload):
        url = "%s/%s" % (self.baseurl, path)
        response = requests.post(url,
                                 verify=False,
                                 headers={'Content-Type': 'application/json'},
                                 data=rest_encoder.encode(payload),
                                 auth=requests.auth.HTTPBasicAuth(self.username, self.password))
        return self._process_response(response)

    def rest_put(self, path, payload):
        url = "%s/%s" % (self.baseurl, path)
        response = requests.put(url,
                                verify=False,
                                headers={'Content-Type': 'application/json'},
                                data=rest_encoder.encode(payload),
                                auth=requests.auth.HTTPBasicAuth(self.username, self.password))
        return self._process_response(response)

    def rest_delete(self, path):
        url = "%s/%s" % (self.baseurl, path)
        response = requests.delete(url,
                                   verify=False,
                                   headers={'Content-Type': 'application/json'},
                                   auth=requests.auth.HTTPBasicAuth(self.username, self.password))
        return self._process_response(response)

    def _process_response(self, response):
        status_code = response.status_code
        body = response.text

        if status_code > 299 or status_code < 200:
            raise RestWsRequestFailedException(status_code, body)

        try:
            body = rest_encoder.decode(body)
        except:
            pass

        return RestResponse(status_code, body)


class RestWsRequestFailedException(Exception):

    code = 0
    body = ""

    def __init__(self, code, body):
        Exception.__init__(self, "%s %s" % (code, body))
        self.code = code
        self.body = body


class RestWsInvalidDataException(Exception):

    code = 0
    body = ""

    def __init__(self, code, body):
        self.code = code
        self.body = body


class RestResponse(object):

    status = 0
    data = ""

    def __init__(self, status, data):
        self.status = status
        self.data = data
