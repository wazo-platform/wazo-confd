# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re
import requests

from pprint import pformat
from hamcrest import (
    all_of,
    anything,
    assert_that,
    equal_to,
    has_entries,
    has_entry,
    has_item,
)


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

    def assert_request(self, path, method='GET', query=None, body=None, json=None):
        results = self.requests_matching(path, method)
        if query:
            assert_that(results, has_item(has_entry('query', has_entries(query))), pformat(results))
        if body:
            assert_that(results, has_item(has_entry('body', equal_to(body))), pformat(results))
        if json:
            assert_that(results, has_item(has_entry('json', equal_to(json))), pformat(results))

    def assert_no_request(self, path, method='GET', query=None, body=None, json=None):
        try:
            results = self.requests_matching(path, method)
        except AssertionError:
            return
        if query:
            query_matcher = has_entry('query', has_entries(query))
        else:
            query_matcher = anything()
        if body:
            body_matcher = has_entry('body', equal_to(body))
        else:
            body_matcher = anything()
        if json:
            json_matcher = has_entry('json', equal_to(json))
        else:
            json_matcher = anything()

        assert_that(results, not(has_item(all_of(query_matcher, body_matcher, json_matcher), pformat(results))))

    def requests_matching(self, path, method='GET'):
        regex = re.compile(path)
        results = [request for request in self.requests()
                   if regex.match(request['path']) and request['method'] == method]

        if not results:
            raise AssertionError("Request not found: {} {}".format(method, path))
        return results
