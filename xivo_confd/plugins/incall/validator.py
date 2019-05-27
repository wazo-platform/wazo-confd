# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_confd.helpers.destination import DestinationValidator
from xivo_confd.helpers.validator import (Validator,
                                          ValidationGroup)


class IncallModelValidator(Validator):

    def __init__(self, destination_validator):
        self._destination_validator = destination_validator

    def validate(self, incall):
        self._destination_validator.validate(incall.destination)


def build_validator():
    incall_validator = IncallModelValidator(DestinationValidator())

    return ValidationGroup(
        create=[incall_validator],
        edit=[incall_validator],
    )
