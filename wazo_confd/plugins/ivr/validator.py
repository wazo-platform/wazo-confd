# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from wazo_confd.helpers.destination import DestinationValidator
from wazo_confd.helpers.validator import (Validator,
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
