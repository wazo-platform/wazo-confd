# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.paging.event import (
    CreatePagingEvent,
    DeletePagingEvent,
    EditPagingEvent,
)

from ..notifier import PagingNotifier


class TestPagingNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.paging = Mock(id=1234)

        self.notifier = PagingNotifier(self.bus)

    def test_when_paging_created_then_event_sent_on_bus(self):
        expected_event = CreatePagingEvent(self.paging.id)

        self.notifier.created(self.paging)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_paging_edited_then_event_sent_on_bus(self):
        expected_event = EditPagingEvent(self.paging.id)

        self.notifier.edited(self.paging)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_paging_deleted_then_event_sent_on_bus(self):
        expected_event = DeletePagingEvent(self.paging.id)

        self.notifier.deleted(self.paging)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
