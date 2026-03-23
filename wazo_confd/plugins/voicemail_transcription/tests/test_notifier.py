# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_bus.resources.voicemail_transcription_config.event import (
    VoicemailTranscriptionConfigEditedEvent,
)

from ..notifier import VoicemailTranscriptionNotifier
from ..types import VoicemailTranscriptionConfigDict


class TestVoicemailTranscriptionNotifier(unittest.TestCase):
    def setUp(self) -> None:
        self.bus = Mock()
        self.notifier = VoicemailTranscriptionNotifier(self.bus)

    def test_when_config_edited_then_event_sent_on_bus(self) -> None:
        tenant_uuid = 'some-tenant-uuid'
        form: VoicemailTranscriptionConfigDict = {'enabled': True}

        expected_event = VoicemailTranscriptionConfigEditedEvent(
            {'enabled': True},
            'some-tenant-uuid',
        )

        self.notifier.edited(tenant_uuid, form)

        self.bus.queue_event.assert_called_once_with(expected_event)
