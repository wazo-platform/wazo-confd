# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import re
import requests

from pprint import pformat
from hamcrest import assert_that, has_entries, equal_to, has_item, has_entry


class SysconfdMock(object):

    def __init__(self, url):
        self.base_url = url

    def clear(self):
        self.clear_requests()

    def clear_requests(self):
        url = "{}/_requests".format(self.base_url)
        response = requests.delete(url)
        response.raise_for_status()

    def requests(self):
        url = "{}/_requests".format(self.base_url)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['requests']

    def assert_request(self, path, method='GET', query=None, body=None):
        results = self.requests_matching(path, method)
        if query:
            assert_that(results, has_item(has_entry('query', has_entries(query))), pformat(results))
        if body:
            assert_that(results, has_item(has_entry('body', equal_to(body))), pformat(results))

    def requests_matching(self, path, method='GET'):
        regex = re.compile(path)
        results = [request for request in self.requests()
                   if regex.match(request['path']) and request['method'] == method]

        if not results:
            raise AssertionError("Request not found: {} {}".format(method, path))
        return results
