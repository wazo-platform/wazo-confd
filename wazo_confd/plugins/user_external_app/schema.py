# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length, OneOf

from wazo_confd.helpers.mallow import BaseSchema


class GETQueryStringSchema(BaseSchema):
    view = fields.String(validate=OneOf(['fallback']), load_default=None)


class UserExternalAppSchema(BaseSchema):
    name = fields.String(dump_only=True)
    label = fields.String(validate=Length(max=256), allow_none=True)
    configuration = fields.Dict(allow_none=True)


class UserExternalAppNameSchema(BaseSchema):
    name = fields.String(validate=Length(max=128))
