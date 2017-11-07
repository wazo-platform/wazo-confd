# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.trunk.event import (CreateTrunkEvent,
                                            EditTrunkEvent,
                                            DeleteTrunkEvent)

from xivo_confd.plugins.trunk.notifier import TrunkNotifier

from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk


class TestTrunkNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.trunk = Mock(Trunk, id=1234)

        self.notifier = TrunkNotifier(self.bus, self.sysconfd)

    def test_when_trunk_created_then_event_sent_on_bus(self):
        expected_event = CreateTrunkEvent(self.trunk.id)

        self.notifier.created(self.trunk)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_trunk_edited_then_event_sent_on_bus(self):
        expected_event = EditTrunkEvent(self.trunk.id)

        self.notifier.edited(self.trunk)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_trunk_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteTrunkEvent(self.trunk.id)

        self.notifier.deleted(self.trunk)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_trunk_sip_edited_then_sip_reloaded(self):
        self.trunk.endpoint = 'sip'

        self.notifier.edited(self.trunk)

        self.sysconfd.exec_request_handlers.assert_called_once_with(self._sysconfd_handlers())

    def test_when_trunk_iax_edited_then_iax_reloaded(self):
        self.trunk.endpoint = 'iax'

        self.notifier.edited(self.trunk)

        self.sysconfd.exec_request_handlers.assert_called_once_with(self._sysconfd_handlers())

    def test_when_trunk_custom_edited_then_no_reload(self):
        self.trunk.endpoint = 'custom'

        self.notifier.edited(self.trunk)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_when_trunk_without_endpoint_edited_then_no_reload(self):
        self.notifier.edited(self.trunk)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_when_trunk_sip_deleted_then_sip_reloaded(self):
        self.trunk.endpoint = 'sip'

        self.notifier.deleted(self.trunk)

        self.sysconfd.exec_request_handlers.assert_called_once_with(self._sysconfd_handlers())

    def test_when_trunk_iax_deleted_then_iax_reloaded(self):
        self.trunk.endpoint = 'iax'

        self.notifier.deleted(self.trunk)

        self.sysconfd.exec_request_handlers.assert_called_once_with(self._sysconfd_handlers())

    def test_when_trunk_custom_deleted_then_no_reload(self):
        self.trunk.endpoint = 'custom'

        self.notifier.deleted(self.trunk)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_when_trunk_without_endpoint_deleted_then_no_reload(self):
        self.notifier.deleted(self.trunk)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def _sysconfd_handlers(self):
        if self.trunk.endpoint == 'sip':
            ipbx_commands = ['sip reload']
        elif self.trunk.endpoint == 'iax':
            ipbx_commands = ['iax2 reload']
        else:
            raise AssertionError('no sysconfd handlers for endpoint {}'.format(self.trunk.endpoint))
        return {
            'ctibus': [],
            'ipbx': ipbx_commands,
            'agentbus': []
        }
