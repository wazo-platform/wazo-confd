# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo_confd.helpers.mallow import BaseSchema


class TenantSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    sip_templates_generated = fields.Boolean(dump_only=True)
    global_sip_template_uuid = fields.UUID(dump_only=True)
    webrtc_sip_template_uuid = fields.UUID(dump_only=True)
    webrtc_video_sip_template_uuid = fields.UUID(dump_only=True)
    registration_trunk_sip_template_uuid = fields.UUID(dump_only=True)
