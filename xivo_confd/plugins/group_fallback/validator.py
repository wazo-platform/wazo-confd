# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.destination import DestinationValidator
from xivo_confd.helpers.validator import Validator, ValidationGroup


class GroupFallbackValidator(Validator):

    def __init__(self, destination_validator):
        self._destination_validator = destination_validator

    def validate(self, fallbacks):
        for fallback in fallbacks.values():
            if fallback is not None:
                self._destination_validator.validate(fallback)


def build_validator():
    fallbacks_validator = GroupFallbackValidator(DestinationValidator())

    return ValidationGroup(
        edit=[fallbacks_validator]
    )
