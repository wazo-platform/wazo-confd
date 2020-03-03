# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length, Regexp
from wazo_confd.helpers.mallow import BaseSchema

ASTERISK_SECTION_NAME_REGEX = r"^[a-zA-Z0-9-_]*$"
ASTERISK_OPTION_VALUE_NAME_REGEX = r"^[a-zA-Z0-9-_\/\.:]*$"


class PJSIPTransportSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    name = fields.String(
        validate=(Regexp(ASTERISK_SECTION_NAME_REGEX), Length(max=128)), required=True,
    )
    options = fields.List(
        fields.List(
            fields.String(
                validate=(
                    Length(min=1, max=4092),
                    Regexp(ASTERISK_OPTION_VALUE_NAME_REGEX),
                )
            ),
            validate=Length(min=2, max=2),
        ),
        many=True,
        required=True,
        validate=Length(max=128),
    )
