# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import deque

from xivo_bus.mixins import PublisherMixin, WazoEventMixin
from xivo_bus.base import Base


class FlushMixin:
    __saved_state = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__deque = deque()

    def queue_event(self, event, *, extra_headers=None, routing_key_override=None):
        self.__deque.append((event, extra_headers, routing_key_override))

    def flush(self):
        while self.__deque:
            event, extra_headers, routing_key = self.__deque.popleft()
            self.publish(event, headers=extra_headers, routing_key=routing_key)

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
    def from_config(cls, config):
        uuid = config['uuid']
        bus = config['bus']
        return cls(name='wazo-confd', service_uuid=uuid, **bus)
