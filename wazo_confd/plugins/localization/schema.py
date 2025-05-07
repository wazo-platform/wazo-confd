# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pycountry
from marshmallow import validates
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length
from xivo.mallow import fields

from wazo_confd.helpers.mallow import BaseSchema


class LocalizationSchema(BaseSchema):
    tenant_uuid = fields.String(dump_only=True, allow_none=False, attribute='uuid')
    country = fields.String(allow_none=True, default=None, validate=Length(equal=2))

    @validates('country')
    def _validate_country(self, country, **kwargs):
        if not country:
            return

        try:
            country_iso = pycountry.countries.get(alpha_2=country)
        except LookupError:  # invalid country format raises this error
            country_iso = None

        if not country_iso:
            raise ValidationError(f'Invalid country code: {country}')
