# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.entity.event import (
    CreateEntityEvent,
    DeleteEntityEvent,
    EditEntityEvent,
)
from xivo_dao.alchemy.entity import Entity

from ..notifier import EntityNotifier


class TestEntityNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.entity = Mock(Entity, id=1234)

        self.notifier = EntityNotifier(self.bus)

    def test_when_entity_created_then_event_sent_on_bus(self):
        expected_event = CreateEntityEvent(self.entity.id)

        self.notifier.created(self.entity)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_entity_edited_then_event_sent_on_bus(self):
        expected_event = EditEntityEvent(self.entity.id)

        self.notifier.edited(self.entity)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_entity_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteEntityEvent(self.entity.id)

        self.notifier.deleted(self.entity)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
