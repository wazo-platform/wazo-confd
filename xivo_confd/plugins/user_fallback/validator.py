# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_confd.helpers.destination import DestinationValidator
from xivo_confd.helpers.validator import Validator, ValidationGroup


class UserFallbackValidator(Validator):

    def __init__(self, destination_validator):
        self._destination_validator = destination_validator

    def validate(self, user):
        for fallback in user.fallbacks.values():
            self._destination_validator.validate(fallback)


def build_validator():
    fallbacks_validator = UserFallbackValidator(DestinationValidator())

    return ValidationGroup(
        edit=[fallbacks_validator]
    )
