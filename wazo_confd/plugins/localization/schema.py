# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pycountry

from marshmallow import validates
from marshmallow.validate import Length
from marshmallow.exceptions import ValidationError
from wazo.mallow import fields

from wazo_confd.helpers.mallow import BaseSchema


class LocalizationSchema(BaseSchema):
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
