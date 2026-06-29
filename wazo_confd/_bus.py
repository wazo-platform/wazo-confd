# Copyright 2015-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import logging
import socket
import threading
from collections import deque
from typing import TYPE_CHECKING, Any, TypeAlias

from wazo_bus.base import Base
from wazo_bus.consumer import BusConsumer as Consumer
from wazo_bus.mixins import PublisherMixin, WazoEventMixin
from xivo.status import Status

logger = logging.getLogger(__name__)

STATUS_IPC_ADDRESS = '\0wazo-confd-status'
STATUS_IPC_TIMEOUT = 2.0
_STATUS_IPC_ACCEPT_TIMEOUT = 0.5
_STATUS_IPC_RECV_SIZE = 4096

if TYPE_CHECKING:
    _FlushMixinBase: TypeAlias = PublisherMixin
else:
    _FlushMixinBase: TypeAlias = object


class FlushMixin(_FlushMixinBase):
    __saved_state: dict[str, Any] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__deque: deque[tuple[Any, dict[str, str] | None]] = deque()

    def queue_event(self, event, *, extra_headers=None):
        self.__deque.append((event, extra_headers))

    def flush(self):
        while self.__deque:
            event, extra_headers = self.__deque.popleft()
            self.publish(event, headers=extra_headers)

    def rollback(self):
        self.__deque.clear()

    def set_as_reference(self):
        type(self).__saved_state = self.__dict__

    @classmethod
    def from_reference(cls):
        if not cls.__saved_state:
            raise ValueError('a reference must be set before using this constructor')

        obj = cls.__new__(cls)
        obj.__dict__ = dict(cls.__saved_state)
        obj.__deque = deque()
        return obj


class BusPublisher(WazoEventMixin, FlushMixin, PublisherMixin, Base):
    @classmethod
    def from_config(cls, service_uuid, bus_config):
        return cls(name='wazo-confd', service_uuid=service_uuid, **bus_config)


class _StatusIPCServer:
    def __init__(self, status_provider):
        self._status_provider = status_provider
        self._stopping = threading.Event()
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._thread = threading.Thread(
            target=self._serve, name='wazo-confd-status-ipc', daemon=True
        )

    def start(self):
        self._thread.start()

    def _serve(self):
        try:
            self._socket.bind(STATUS_IPC_ADDRESS)
            self._socket.listen()
            self._socket.settimeout(_STATUS_IPC_ACCEPT_TIMEOUT)
        except OSError:
            if self._stopping.is_set():
                return
            logger.exception(
                'Could not start status IPC server; workers will report '
                'bus_consumer as failed'
            )
            return
        while not self._stopping.is_set():
            try:
                conn, _ = self._socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            with conn:
                try:
                    status: dict[str, Any] = {'bus_consumer': {}}
                    self._status_provider(status)
                    conn.sendall(json.dumps(status).encode('utf-8'))
                except OSError:
                    logger.debug('status IPC client disconnected', exc_info=True)

    def stop(self):
        self._stopping.set()
        self._socket.close()
        self._thread.join(timeout=2)

    @staticmethod
    def read() -> dict[str, Any]:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(STATUS_IPC_TIMEOUT)
            sock.connect(STATUS_IPC_ADDRESS)
            payload = b''.join(iter(lambda: sock.recv(_STATUS_IPC_RECV_SIZE), b''))
        return json.loads(payload)


class BusConsumer(Consumer):
    @classmethod
    def from_config(cls, bus_config):
        return cls(name='wazo-confd', **bus_config)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status_server = _StatusIPCServer(self.provide_status)

    def provide_status(self, status):
        status['bus_consumer']['status'] = (
            Status.ok if self.consumer_connected() else Status.fail
        )

    def __enter__(self):
        self._status_server.start()
        return super().__enter__()

    def __exit__(self, *args):
        self._status_server.stop()
        return super().__exit__(*args)


class NoopConsumer:
    @classmethod
    def from_config(cls, bus_config: Any) -> NoopConsumer:
        return cls()

    def subscribe(self, *args: Any, **kwargs: Any) -> None:
        pass

    def provide_status(self, status: Any) -> None:
        try:
            remote = _StatusIPCServer.read()
            status['bus_consumer']['status'] = remote['bus_consumer']['status']
        except (OSError, ValueError, KeyError):
            logger.warning(
                'Could not read bus_consumer status from the main wazo-confd '
                'process; reporting it as failed',
                exc_info=True,
            )
            status['bus_consumer']['status'] = Status.fail

    def __enter__(self) -> NoopConsumer:
        return self

    def __exit__(self, *args: Any) -> None:
        return None
