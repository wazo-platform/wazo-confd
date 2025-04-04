# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.trunk.event import (
    TrunkCreatedEvent,
    TrunkDeletedEvent,
    TrunkEditedEvent,
)
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk

from ..notifier import TrunkNotifier


class TestTrunkNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.trunk = Mock(
            Trunk,
            id=1234,
            endpoint_sip_uuid=None,
            endpoint_iax_id=None,
            endpoint_custom_id=None,
            tenant_uuid=uuid4(),
        )

        self.notifier = TrunkNotifier(self.bus, self.sysconfd)

    def test_when_trunk_created_then_event_sent_on_bus(self):
        expected_event = TrunkCreatedEvent(self.trunk.id, self.trunk.tenant_uuid)

        self.notifier.created(self.trunk)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_trunk_edited_then_event_sent_on_bus(self):
        expected_event = TrunkEditedEvent(self.trunk.id, self.trunk.tenant_uuid)

        self.notifier.edited(self.trunk)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_trunk_deleted_then_event_sent_on_bus(self):
        expected_event = TrunkDeletedEvent(self.trunk.id, self.trunk.tenant_uuid)

        self.notifier.deleted(self.trunk)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_trunk_sip_edited_then_sip_reloaded(self):
        self.trunk.endpoint_sip_uuid = 123

        self.notifier.edited(self.trunk)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            self._sysconfd_handlers()
        )

    def test_when_trunk_iax_edited_then_iax_reloaded(self):
        self.trunk.endpoint_iax_id = 123

        self.notifier.edited(self.trunk)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            self._sysconfd_handlers()
        )

    def test_when_trunk_custom_edited_then_no_reload(self):
        self.trunk.endpoint_custom_id = 123

        self.notifier.edited(self.trunk)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_when_trunk_without_endpoint_edited_then_no_reload(self):
        self.notifier.edited(self.trunk)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_when_trunk_sip_deleted_then_sip_reloaded(self):
        self.trunk.endpoint_sip_uuid = 123

        self.notifier.deleted(self.trunk)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            self._sysconfd_handlers()
        )

    def test_when_trunk_iax_deleted_then_iax_reloaded(self):
        self.trunk.endpoint_iax_id = 123

        self.notifier.deleted(self.trunk)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            self._sysconfd_handlers()
        )

    def test_when_trunk_custom_deleted_then_no_reload(self):
        self.trunk.endpoint_custom_id = 123

        self.notifier.deleted(self.trunk)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_when_trunk_without_endpoint_deleted_then_no_reload(self):
        self.notifier.deleted(self.trunk)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def _sysconfd_handlers(self):
        if self.trunk.endpoint_sip_uuid:
            ipbx_commands = ['module reload res_pjsip.so']
        elif self.trunk.endpoint_iax_id:
            ipbx_commands = ['iax2 reload']
        else:
            raise AssertionError(
                'no sysconfd handlers for endpoint {}'.format(self.trunk.endpoint)
            )
        return {'ipbx': ipbx_commands}
