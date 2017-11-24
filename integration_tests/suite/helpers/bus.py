# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_test_helpers import bus


class BusClientWrapper(object):

    def __init__(self):
        self.host = None
        self.port = None
        self._bus = None

    def __getattr__(self, attr):
        if self._bus is None:
            self._bus = self._create_client()
        return getattr(self._bus, attr)

    def _create_client(self):
        return bus.BusClient.from_connection_fields(host=self.host, port=self.port)


BusClient = BusClientWrapper()


def setup_bus(host, port):
    BusClient.host = host
    BusClient.port = port
