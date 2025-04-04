# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid
from unittest.mock import Mock

from wazo_bus.resources.line_application.event import (
    LineApplicationAssociatedEvent,
    LineApplicationDissociatedEvent,
)
from xivo_dao.alchemy.application import Application
from xivo_dao.alchemy.linefeatures import LineFeatures as Line

from ..notifier import LineApplicationNotifier


class TestLineApplicationNotifier(unittest.TestCase):
    REQUEST_HANDLERS = {'ipbx': ['module reload res_pjsip.so']}

    def setUp(self):
        self.sysconfd = Mock()
        self.line = Mock(
            Line,
            id=1,
            endpoint_sip={'uuid': str(uuid.uuid4())},
            endpoint_sccp=None,
            endpoint_custom=None,
            tenant_uuid=uuid.uuid4(),
        )
        self.line.name = 'limitation of mock instantiation with name ...'
        self.application = Mock(Application, uuid='custom-uuid')
        self.bus = Mock()
        self.notifier = LineApplicationNotifier(self.bus, self.sysconfd)

    def test_associate_then_pjsip_reloaded(self):
        self.notifier.associated(self.line, self.application)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            self.REQUEST_HANDLERS
        )

    def test_dissociate_then_pjsip_reloaded(self):
        self.notifier.dissociated(self.line, self.application)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            self.REQUEST_HANDLERS
        )

    def test_associate_then_bus_event(self):
        expected_event = LineApplicationAssociatedEvent(
            {
                'id': self.line.id,
                'name': self.line.name,
                'endpoint_sip': self.line.endpoint_sip,
                'endpoint_sccp': self.line.endpoint_sccp,
                'endpoint_custom': self.line.endpoint_custom,
            },
            {'uuid': self.application.uuid},
            self.line.tenant_uuid,
        )

        self.notifier.associated(self.line, self.application)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_dissociate_then_bus_event(self):
        expected_event = LineApplicationDissociatedEvent(
            {
                'id': self.line.id,
                'name': self.line.name,
                'endpoint_sip': self.line.endpoint_sip,
                'endpoint_sccp': self.line.endpoint_sccp,
                'endpoint_custom': self.line.endpoint_custom,
            },
            {'uuid': self.application.uuid},
            self.line.tenant_uuid,
        )

        self.notifier.dissociated(self.line, self.application)

        self.bus.queue_event.assert_called_once_with(expected_event)
