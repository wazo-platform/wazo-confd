# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.entity.event import (CreateEntityEvent,
                                             EditEntityEvent,
                                             DeleteEntityEvent)

from xivo_confd.plugins.entity.notifier import EntityNotifier

from xivo_dao.alchemy.entity import Entity


class TestEntityNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.entity = Mock(Entity, id=1234)

        self.notifier = EntityNotifier(self.bus)

    def test_when_entity_created_then_event_sent_on_bus(self):
        expected_event = CreateEntityEvent(self.entity.id)

        self.notifier.created(self.entity)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_entity_edited_then_event_sent_on_bus(self):
        expected_event = EditEntityEvent(self.entity.id)

        self.notifier.edited(self.entity)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_entity_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteEntityEvent(self.entity.id)

        self.notifier.deleted(self.entity)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
