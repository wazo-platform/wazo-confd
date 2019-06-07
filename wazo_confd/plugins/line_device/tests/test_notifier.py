# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from hamcrest import assert_that, equal_to

from xivo_bus.resources.line_device.event import (
    LineDeviceAssociatedEvent,
    LineDeviceDissociatedEvent,
)
from xivo_dao.alchemy.linefeatures import LineFeatures as Line

from wazo_confd.plugins.device.model import Device

from ..notifier import LineDeviceNotifier


class TestLineDeviceNotifier(unittest.TestCase):

    REQUEST_HANDLERS = {
        'ipbx': ['module reload chan_sccp.so'],
        'agentbus': [],
    }

    def setUp(self):
        self.sysconfd = Mock()
        self.line = Mock(
            Line,
            id=1,
            endpoint_sip={'id': 2},
            endpoint_sccp=None,
            endpoint_custom=None,
        )
        self.line.name = 'limitation of mock instantiation with name ...'
        self.device = Mock(Device, id='custom-id')
        self.bus = Mock()
        self.notifier = LineDeviceNotifier(self.bus, self.sysconfd)

    def test_given_line_is_not_sccp_when_associated_then_sccp_not_reloaded(self):
        self.line.endpoint = "sip"
        self.notifier.associated(self.line, self.device)

        assert_that(self.sysconfd.exec_request_handlers.call_count, equal_to(0))

    def test_given_line_is_not_sccp_when_dissociated_then_sccp_not_reloaded(self):
        self.line.endpoint = "sip"
        self.notifier.dissociated(self.line, self.device)

        assert_that(self.sysconfd.exec_request_handlers.call_count, equal_to(0))

    def test_given_line_is_sccp_when_associated_then_sccp_reloaded(self):
        self.line.endpoint = "sccp"
        self.notifier.associated(self.line, self.device)

        self.sysconfd.exec_request_handlers.assert_called_once_with(self.REQUEST_HANDLERS)

    def test_given_line_is_sccp_when_dissociated_then_sccp_reloaded(self):
        self.line.endpoint = "sccp"
        self.notifier.dissociated(self.line, self.device)

        self.sysconfd.exec_request_handlers.assert_called_once_with(self.REQUEST_HANDLERS)

    def test_associate_then_bus_event(self):
        expected_event = LineDeviceAssociatedEvent(
            line={
                'id': self.line.id,
                'name': self.line.name,
                'endpoint_sip': self.line.endpoint_sip,
                'endpoint_sccp': self.line.endpoint_sccp,
                'endpoint_custom': self.line.endpoint_custom,
            },
            device={'id': self.device.id}
        )

        self.notifier.associated(self.line, self.device)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_then_bus_event(self):
        expected_event = LineDeviceDissociatedEvent(
            line={
                'id': self.line.id,
                'name': self.line.name,
                'endpoint_sip': self.line.endpoint_sip,
                'endpoint_sccp': self.line.endpoint_sccp,
                'endpoint_custom': self.line.endpoint_custom,
            },
            device={'id': self.device.id}
        )

        self.notifier.dissociated(self.line, self.device)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
