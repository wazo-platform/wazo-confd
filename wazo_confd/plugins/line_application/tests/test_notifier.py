# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from xivo_bus.resources.line_application.event import (
    LineApplicationAssociatedEvent,
    LineApplicationDissociatedEvent,
)
from xivo_dao.alchemy.application import Application
from xivo_dao.alchemy.linefeatures import LineFeatures as Line

from ..notifier import LineApplicationNotifier


class TestLineApplicationNotifier(unittest.TestCase):

    REQUEST_HANDLERS = {'ipbx': ['module reload res_pjsip.so'], 'agentbus': []}

    def setUp(self):
        self.sysconfd = Mock()
        self.line = Mock(
            Line, id=1, endpoint_sip={'id': 2}, endpoint_sccp=None, endpoint_custom=None
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
            line={
                'id': self.line.id,
                'name': self.line.name,
                'endpoint_sip': self.line.endpoint_sip,
                'endpoint_sccp': self.line.endpoint_sccp,
                'endpoint_custom': self.line.endpoint_custom,
            },
            application={'uuid': self.application.uuid},
        )

        self.notifier.associated(self.line, self.application)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_then_bus_event(self):
        expected_event = LineApplicationDissociatedEvent(
            line={
                'id': self.line.id,
                'name': self.line.name,
                'endpoint_sip': self.line.endpoint_sip,
                'endpoint_sccp': self.line.endpoint_sccp,
                'endpoint_custom': self.line.endpoint_custom,
            },
            application={'uuid': self.application.uuid},
        )

        self.notifier.dissociated(self.line, self.application)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
