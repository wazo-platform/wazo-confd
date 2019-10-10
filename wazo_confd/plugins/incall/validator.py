# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.destination import DestinationValidator
from wazo_confd.helpers.validator import Validator, ValidationGroup


class IncallModelValidator(Validator):
    def __init__(self, destination_validator):
        self._destination_validator = destination_validator

    def validate(self, incall):
        self._destination_validator.validate(incall.destination)


def build_validator():
    incall_validator = IncallModelValidator(DestinationValidator())

    return ValidationGroup(create=[incall_validator], edit=[incall_validator])
