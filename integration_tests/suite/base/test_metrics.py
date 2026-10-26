# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests
from hamcrest import assert_that, contains_string, equal_to

from . import BaseIntegrationTest, confd


def test_metrics_without_token():
    confd.infos.get()
    confd_port = BaseIntegrationTest.service_port(9486, 'confd')

    response = requests.get(f'http://127.0.0.1:{confd_port}/1.1/metrics')

    assert_that(response.status_code, equal_to(200))
    assert_that(
        response.text,
        contains_string('flask_http_request_total{method="GET",status="200"}'),
    )
    assert_that(
        response.text,
        contains_string(
            'flask_http_request_duration_seconds_count'
            '{endpoint="info",method="GET",status="200"}'
        ),
    )
