# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.mallow import fields

from wazo_confd.helpers.mallow import BaseSchema


class LocalizationSchema(BaseSchema):
    country = fields.String(allow_none=True, default=None)
