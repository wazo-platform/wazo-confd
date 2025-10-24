# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from xivo.tenant_flask_helpers import Tenant

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource, build_tenant

from .schema import RecordingAnnouncementSchema


class RecordingsAnnouncementsResource(ConfdResource):
    schema = RecordingAnnouncementSchema

    def __init__(self, service):
        self.service = service

    @required_acl('confd.recordings.announcements.read')
    def get(self):
        tenant = Tenant.autodetect()
        model = self.service.get(tenant.uuid)
        return self.schema().dump(model)

    @required_acl('confd.recordings.announcements.update')
    def put(self):
        tenant_uuid = build_tenant()
        model = self.service.get(tenant_uuid)
        self._parse_and_update(model)
        return '', 204

    def _parse_and_update(self, model, **kwargs):
        form = self.schema().load(request.get_json(force=True), partial=True)
        for name, value in form.items():
            setattr(model, name, value)
        self.service.edit(model, **kwargs)
