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

import requests
from acceptance.helpers.config import get_config_value
from xivo_restapi.helpers import serializer


class WsUtils(object):
    '''
    This helper class is a forerunner of a library
    proposing methods for easy implementation of
    REST web services
    '''

    def __init__(self, api_version=None):
        self.baseurl = self._prepare_baseurl(api_version)
        self.auth = self._prepare_auth()
        self.session = requests.Session()

    def _prepare_baseurl(self, api_version=None):
        hostname = get_config_value('xivo', 'hostname')
        protocol = get_config_value('restapi', 'protocol')
        port = get_config_value('restapi', 'port')
        api_version = api_version or get_config_value('restapi', 'api_version')

        baseurl = "%s://%s:%s/%s" % (protocol, hostname, port, api_version)
        return baseurl

    def _prepare_auth(self):
        username = get_config_value('restapi', 'username')
        password = get_config_value('restapi', 'password')

        auth = requests.auth.HTTPDigestAuth(username, password)
        return auth

    def rest_get(self, path, **kwargs):
        request = self._prepare_request('GET', path, **kwargs)
        return self._process_request(request)

    def rest_post(self, path, payload, **kwargs):
        data = serializer.encode(payload)
        request = self._prepare_request('POST', path, data=data, **kwargs)
        return self._process_request(request)

    def rest_put(self, path, payload, **kwargs):
        data = serializer.encode(payload)
        request = self._prepare_request('PUT', path, data=data, **kwargs)
        return self._process_request(request)

    def rest_delete(self, path, **kwargs):
        request = self._prepare_request('DELETE', path, **kwargs)
        return self._process_request(request)

    def _prepare_request(self, method, path, **kwargs):
        headers = {'Content-Type': 'application/json'}
        url = "%s/%s" % (self.baseurl, path)

        return requests.Request(method=method,
                                url=url,
                                headers=headers,
                                auth=self.auth,
                                **kwargs)

    def _process_request(self, request):
        prep = request.prepare()
        response = self.session.send(prep, verify=False, allow_redirects=False)
        return self._process_response(response)

    def _process_response(self, response):
        status_code = response.status_code
        body = response.text
        headers = response.headers

        try:
            body = serializer.decode(body)
        except:
            pass

        return RestResponse(status_code, headers, body)


class RestResponse(object):

    def __init__(self, status, headers, data):
        self.status = status
        self.headers = headers
        self.data = data
