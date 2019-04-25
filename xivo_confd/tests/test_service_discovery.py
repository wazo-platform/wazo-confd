# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import assert_that, equal_to
from mock import ANY, Mock, patch

from ..service_discovery import self_check


class TestSelfCheck(unittest.TestCase):

    def setUp(self):
        self.https_port = 4243
        self.config = {'rest_api': {'port': self.https_port,
                                    'certificate': 'my-certificate'}}

    @patch('xivo_confd.service_discovery.requests.get', return_value=Mock(status_code=404))
    def test_that_self_check_returns_false_if_infos_does_not_return_200(self, get):
        result = self_check(self.config)

        assert_that(result, equal_to(False))

        self.assert_get_called(get, 'https://localhost:4243/1.1/infos')

    @patch('xivo_confd.service_discovery.requests.get', return_value=Mock(status_code=200))
    def test_that_self_check_returns_true_if_infos_returns_200(self, get):
        result = self_check(self.config)

        assert_that(result, equal_to(True))

        self.assert_get_called(get, 'https://localhost:4243/1.1/infos')

    @patch('xivo_confd.service_discovery.requests.get', return_value=Mock(status_code=401))
    def test_that_self_check_returns_true_if_infos_returns_401(self, get):
        result = self_check(self.config)

        assert_that(result, equal_to(True))

        self.assert_get_called(get, 'https://localhost:4243/1.1/infos')

    @patch('xivo_confd.service_discovery.requests.get', side_effect=Exception)
    def test_that_self_check_returns_false_on_exception(self, get):
        result = self_check(self.config)

        assert_that(result, equal_to(False))

        self.assert_get_called(get, 'https://localhost:4243/1.1/infos')

    def assert_get_called(self, get, url):
        get.assert_called_once_with(url, headers={'accept': 'application/json'}, verify=ANY)
