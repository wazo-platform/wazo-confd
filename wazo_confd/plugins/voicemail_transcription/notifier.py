# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from wazo_bus.resources.voicemail_transcription_config.event import (
    VoicemailTranscriptionConfigEditedEvent,
)

from wazo_confd import bus
from wazo_confd._bus import BusPublisher

if TYPE_CHECKING:
    from .types import VoicemailTranscriptionConfigDict


class VoicemailTranscriptionNotifier:
    def __init__(self, bus: BusPublisher) -> None:
        self.bus = bus

    def edited(self, tenant_uuid: str, form: VoicemailTranscriptionConfigDict) -> None:
        event = VoicemailTranscriptionConfigEditedEvent(
            {'enabled': form['enabled']},
            tenant_uuid,
        )
        self.bus.queue_event(event)


def build_notifier() -> VoicemailTranscriptionNotifier:
    return VoicemailTranscriptionNotifier(bus)
