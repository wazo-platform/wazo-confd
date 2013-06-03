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
from xivo_restapi.restapi_config import RestAPIConfig
import httplib


class WsUtils(object):
    '''
    This helper class is a forerunner of a library
    proposing methods for easy implementation of
    REST web services
    '''

    def __init__(self):
        self.connection = httplib.HTTPConnection(
                            RestAPIConfig.XIVO_RECORD_SERVICE_ADDRESS +
                            ":" +
                            str(RestAPIConfig.XIVO_RECORD_SERVICE_PORT)
                        )
        self.requestURI = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH

    def rest_get(self, serviceURI):
        method = "GET"
        return self._http_request(serviceURI, method)

    def rest_post(self, serviceURI, data):
        method = "POST"
        body = rest_encoder.encode(data)
        return self._http_request(serviceURI, method, body)

    def rest_put(self, serviceURI, data):
        method = "PUT"
        body = rest_encoder.encode(data)
        return self._http_request(serviceURI, method, body)

    def rest_delete(self, serviceURI):
        method = "DELETE"
        return self._http_request(serviceURI, method)

    def _http_request(self, serviceURI, method, body=""):
        headers = RestAPIConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        uri = self.requestURI + serviceURI
        self.connection.request(method, uri, body, headers)
        reply = self.connection.getresponse()
        status = reply.status
        body = reply.read()
        try:
            data = rest_encoder.decode(body)
        except:
            data = body

        if (status > 299 and status < 200):
            raise RestWsRequestFailedException(status, data)
        return RestResponse(status, data)


class RestWsRequestFailedException(Exception):

    code = 0
    body = ""

    def __init__(self, code, body):

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
