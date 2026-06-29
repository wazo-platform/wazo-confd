# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import requests
from wazo_test_helpers import until

from ..helpers.config import TOKEN, WORKERS_ENABLED
from . import BaseIntegrationTest

pytestmark = pytest.mark.skipif(
    not WORKERS_ENABLED,
    reason='requires INTEGRATION_TEST_CONFD_WORKERS >= 1',
)

WORKER_MARKER = 'wazo-confd (http worker) starting...'


def _status_url():
    port = BaseIntegrationTest.service_port(9486, 'confd')
    return f'http://127.0.0.1:{port}/1.1/status'


def test_requests_are_load_balanced_across_main_and_worker():
    url = _status_url()

    def both_instances_served():
        requests.get(url, headers={'X-Auth-Token': TOKEN, 'Connection': 'close'})
        return (
            '/1.1/status' in BaseIntegrationTest.service_logs('confd')
            and '/1.1/status' in BaseIntegrationTest.worker_logs()
        )

    until.true(
        both_instances_served,
        timeout=30,
        message='Requests were not load-balanced across the main process and worker',
    )


def test_only_the_worker_runs_in_http_worker_mode():
    assert WORKER_MARKER in BaseIntegrationTest.worker_logs()
    assert WORKER_MARKER not in BaseIntegrationTest.service_logs('confd')


def test_worker_reports_bus_consumer_status_through_ipc():
    url = _status_url()
    headers = {'X-Auth-Token': TOKEN, 'Connection': 'close'}

    for _ in range(20):
        status = requests.get(url, headers=headers).json()
        assert status.get('bus_consumer', {}).get('status') == 'ok', status
