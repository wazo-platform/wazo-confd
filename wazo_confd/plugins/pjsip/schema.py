# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length
from wazo_confd.helpers.mallow import BaseSchema, PJSIPSection, PJSIPSectionOption


class PJSIPTransportDeleteRequestSchema(BaseSchema):
    fallback = fields.UUID(load_default=None)


class PJSIPTransportSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    name = fields.String(validate=PJSIPSection(), required=True)
    options = fields.List(
        PJSIPSectionOption(),
        validate=Length(max=128),
        load_default=[],
    )
