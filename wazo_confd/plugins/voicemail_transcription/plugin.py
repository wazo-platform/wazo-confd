# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any

from .resource import VoicemailTranscriptionConfig
from .service import build_service


class Plugin:
    def load(self, dependencies: dict[str, Any]) -> None:
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            VoicemailTranscriptionConfig,
            '/voicemails/transcription',
            resource_class_args=(service,),
        )
