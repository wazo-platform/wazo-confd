# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import Any, Tuple

from flask import request

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource, Tenant, build_tenant

from .schema import VoicemailTranscriptionConfigSchema
from .service import VoicemailTranscriptionConfigService


class VoicemailTranscriptionConfig(ConfdResource):
    schema = VoicemailTranscriptionConfigSchema

    def __init__(self, service: VoicemailTranscriptionConfigService) -> None:
        super().__init__()
        self.service = service

    @required_acl('confd.voicemails.transcription.read')
    def get(self) -> dict[str, Any]:
        tenant = Tenant.autodetect()
        config = self.service.get(tenant.uuid)
        return self.schema().dump(config)

    @required_acl('confd.voicemails.transcription.update')
    def put(self) -> Tuple[str, int]:
        tenant = build_tenant()
        form = self.schema().load(request.get_json(force=True))
        self.service.edit(tenant, form)
        return '', 204
