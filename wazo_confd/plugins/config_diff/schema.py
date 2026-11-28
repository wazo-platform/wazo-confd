# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo_confd.helpers.mallow import BaseSchema


class ConfigHistoryLogItemSchema(BaseSchema):
    commit = fields.String()
    date = fields.String()
    files_changed = fields.List(fields.String())


class ConfigHistorySchema(BaseSchema):
    items = fields.List(fields.Nested(ConfigHistoryLogItemSchema))


class ConfigHistoryDiffSchema(BaseSchema):
    item = fields.String()
