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

from xivo_dao.helpers import errors

from xivo_confd.helpers.destination import DestinationValidator
from xivo_confd.helpers.validator import (Validator,
                                          ValidationGroup)


class IvrModelValidator(Validator):

    def __init__(self, destination_validator):
        self._destination_validator = destination_validator

    def validate(self, ivr):
        if ivr.abort_destination:
            self._destination_validator.validate(ivr.abort_destination)
        if ivr.invalid_destination:
            self._destination_validator.validate(ivr.invalid_destination)
        if ivr.timeout_destination:
            self._destination_validator.validate(ivr.timeout_destination)
        extens = set()
        for choice in ivr.choices:
            if choice.exten in extens:
                raise errors.ivr_exten_used(choice.exten)
            extens.add(choice.exten)
            self._destination_validator.validate(choice.destination)


def build_validator():
    ivr_validator = IvrModelValidator(DestinationValidator())

    return ValidationGroup(
        create=[ivr_validator],
        edit=[ivr_validator],
    )
