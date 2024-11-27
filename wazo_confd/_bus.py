# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import deque

from wazo_bus.consumer import BusConsumer as Consumer
from wazo_bus.mixins import PublisherMixin, WazoEventMixin
from wazo_bus.base import Base
from wazo.status import Status


class FlushMixin:
    __saved_state = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__deque = deque()

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


class BusConsumer(Consumer):
    @classmethod
    def from_config(cls, bus_config):
        return cls(name='wazo-confd', **bus_config)

    def provide_status(self, status):
        status['bus_consumer']['status'] = (
            Status.ok if self.consumer_connected() else Status.fail
        )
