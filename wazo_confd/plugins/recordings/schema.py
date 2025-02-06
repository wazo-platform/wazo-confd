# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.mallow import fields

from wazo_confd.helpers.mallow import BaseSchema


class RecordingAnnouncementSchema(BaseSchema):
    recording_start = fields.String(
        attribute='record_start_announcement',
        allow_none=True,
        dump_default=None,
    )
    recording_stop = fields.String(
        attribute='record_stop_announcement',
        allow_none=True,
        dump_default=None,
    )
