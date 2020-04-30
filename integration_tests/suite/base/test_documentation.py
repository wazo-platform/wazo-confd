# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import requests
import unittest
import yaml

from openapi_spec_validator import validate_v2_spec

from . import BaseIntegrationTest

requests.packages.urllib3.disable_warnings()

logger = logging.getLogger('openapi_spec_validator')
logger.setLevel(logging.INFO)


class TestDocumentation(unittest.TestCase):
    def test_documentation_errors(self):
        confd_port = BaseIntegrationTest.service_port(9486, 'confd')
        api_url = 'http://localhost:{port}/1.1/api/api.yml'.format(port=confd_port)
        api = requests.get(api_url)
        validate_v2_spec(yaml.safe_load(api.text))
