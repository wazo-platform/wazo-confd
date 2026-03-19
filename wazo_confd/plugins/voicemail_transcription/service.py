# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from types import ModuleType
from typing import TYPE_CHECKING

from xivo_dao.resources.tenant import dao as tenant_dao

from .notifier import VoicemailTranscriptionNotifier, build_notifier

if TYPE_CHECKING:
    from .types import VoicemailTranscriptionConfigDict


class VoicemailTranscriptionConfigService:
    def __init__(
        self, dao: ModuleType, notifier: VoicemailTranscriptionNotifier
    ) -> None:
        self.dao = dao
        self.notifier = notifier

    def get(self, tenant_uuid: str) -> VoicemailTranscriptionConfigDict:
        tenant = self.dao.get(tenant_uuid)
        return {'enabled': tenant.voicemail_transcription_enabled}

    def edit(self, tenant_uuid: str, form: VoicemailTranscriptionConfigDict) -> None:
        tenant = self.dao.get(tenant_uuid)
        tenant.voicemail_transcription_enabled = form['enabled']
        self.dao.edit(tenant)
        self.notifier.edited(tenant_uuid, form)


def build_service() -> VoicemailTranscriptionConfigService:
    return VoicemailTranscriptionConfigService(tenant_dao, build_notifier())
