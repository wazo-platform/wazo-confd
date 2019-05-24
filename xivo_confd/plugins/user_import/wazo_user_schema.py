# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length, Regexp

from xivo_confd.plugins.user.schema import USERNAME_REGEX, PASSWORD_REGEX
from xivo_confd.helpers.mallow import BaseSchema


class WazoUserSchema(BaseSchema):
    uuid = fields.String()
    firstname = fields.String(validate=Length(max=128), required=True)
    lastname = fields.String(validate=Length(max=128), allow_none=True)
    email_address = fields.String(validate=Length(max=254), allow_none=True)
    username = fields.String(validate=Regexp(USERNAME_REGEX), allow_none=True)
    password = fields.String(validate=Regexp(PASSWORD_REGEX), allow_none=True)
    enabled = fields.Boolean(allow_none=True)
