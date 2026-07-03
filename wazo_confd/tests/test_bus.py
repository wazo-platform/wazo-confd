# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import socket
import time
import unittest
from unittest.mock import Mock, patch

from xivo.status import Status

from wazo_confd import _bus
from wazo_confd._bus import NoopConsumer, _StatusIPCServer


class TestStatusIPCServer(unittest.TestCase):
    def _read_ok(self, address, timeout=3.0):
        deadline = time.monotonic() + timeout
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                with patch.object(_bus, 'STATUS_IPC_ADDRESS', address):
                    return _StatusIPCServer.read()
            except (OSError, ValueError) as e:
                last_error = e
                time.sleep(0.02)
        raise AssertionError(f'server never served a valid status: {last_error!r}')

    def test_read_returns_the_provided_status(self):
        address = '\0wazo-confd-test-roundtrip'

        def provider(status):
            status['bus_consumer']['status'] = Status.ok

        server = _StatusIPCServer(provider)
        with patch.object(_bus, 'STATUS_IPC_ADDRESS', address):
            server.start()
            try:
                result = self._read_ok(address)
            finally:
                server.stop()
        self.assertEqual(result, {'bus_consumer': {'status': Status.ok}})

    def test_serve_survives_non_oserror_from_provider(self):
        address = '\0wazo-confd-test-survive-provider'
        calls: list[int] = []

        def provider(status):
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError('boom')
            status['bus_consumer']['status'] = Status.ok

        server = _StatusIPCServer(provider)
        with patch.object(_bus, 'STATUS_IPC_ADDRESS', address):
            server.start()
            try:
                result = self._read_ok(address)
            finally:
                server.stop()
        self.assertEqual(result['bus_consumer']['status'], Status.ok)
        self.assertGreaterEqual(len(calls), 2)

    def test_serve_survives_transient_accept_error(self):
        server = _StatusIPCServer(Mock())
        accept_calls: list[int] = []

        def fake_accept():
            accept_calls.append(1)
            if len(accept_calls) == 1:
                raise OSError('transient, e.g. EMFILE')
            raise socket.timeout()

        server._socket = Mock()
        server._socket.accept.side_effect = fake_accept

        with patch.object(_bus.time, 'sleep'):
            server.start()
            deadline = time.monotonic() + 2
            while len(accept_calls) < 3 and time.monotonic() < deadline:
                time.sleep(0.01)
            server.stop()

        self.assertGreaterEqual(len(accept_calls), 3)
        self.assertFalse(server._thread.is_alive())


class TestNoopConsumerStatus(unittest.TestCase):
    def test_reports_status_read_from_the_main_process(self):
        consumer = NoopConsumer()
        status: dict = {'bus_consumer': {}}
        with patch.object(
            _StatusIPCServer,
            'read',
            return_value={'bus_consumer': {'status': Status.ok}},
        ):
            consumer.provide_status(status)
        self.assertEqual(status['bus_consumer']['status'], Status.ok)

    def test_reports_fail_when_ipc_is_unreachable(self):
        consumer = NoopConsumer()
        status: dict = {'bus_consumer': {}}
        with patch.object(_StatusIPCServer, 'read', side_effect=OSError('refused')):
            consumer.provide_status(status)
        self.assertEqual(status['bus_consumer']['status'], Status.fail)
