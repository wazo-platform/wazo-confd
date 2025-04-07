# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length, OneOf, Predicate

from wazo_confd.helpers.mallow import BaseSchema
from wazo_confd.helpers.restful import ListSchema as BaseListSchema


class ListSchema(BaseListSchema):
    availability = fields.String(
        load_default='available', validate=OneOf(['available', 'all'])
    )


class ContextRangeSchema(BaseSchema):
    start = fields.String(
        validate=(Predicate('isdigit'), Length(max=16)), required=True
    )
    end = fields.String(validate=(Predicate('isdigit'), Length(max=16)))
