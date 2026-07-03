# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from wazo_test_helpers import until

from ..helpers.config import WORKERS_ENABLED
from . import BaseIntegrationTest, confd

pytestmark = pytest.mark.skipif(
    not WORKERS_ENABLED,
    reason='requires INTEGRATION_TEST_CONFD_WORKERS >= 1',
)

WORKER_MARKER = 'wazo-confd (http worker) starting...'


def test_requests_are_load_balanced_across_main_and_worker():
    def both_instances_served():
        confd.status.get()
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
    def worker_status_count():
        return BaseIntegrationTest.worker_logs().count('/1.1/status')

    baseline = worker_status_count()

    def worker_served_ok_status():
        status = confd.status.get().json['bus_consumer']['status']
        return status == 'ok' and worker_status_count() > baseline

    until.true(
        worker_served_ok_status,
        timeout=30,
        message='Worker never served an ok bus_consumer status through the IPC path',
    )
