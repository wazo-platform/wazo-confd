# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo_confd.helpers.mallow import BaseSchema


class VoicemailTranscriptionConfigSchema(BaseSchema):
    enabled = fields.Boolean(required=True)
