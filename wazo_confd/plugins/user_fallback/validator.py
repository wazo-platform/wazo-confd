# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.destination import DestinationValidator
from wazo_confd.helpers.validator import ValidationGroup, Validator


class UserFallbackValidator(Validator):
    def __init__(self, destination_validator):
        self._destination_validator = destination_validator

    def validate(self, fallbacks):
        for fallback in fallbacks.values():
            if fallback is not None:
                self._destination_validator.validate(fallback)


def build_validator():
    fallbacks_validator = UserFallbackValidator(DestinationValidator())

    return ValidationGroup(edit=[fallbacks_validator])
