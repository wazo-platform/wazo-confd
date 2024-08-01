# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.validator import Validator


class CountryValidator(Validator):
    def validate(self, localization):
        pass


def build_validator():
    return CountryValidator()
