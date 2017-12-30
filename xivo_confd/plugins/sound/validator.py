# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import Validator, ValidationGroup

from .schema import ASTERISK_CATEGORY
from .storage import DEFAULT_DIRECTORIES, RESERVED_DIRECTORIES


class SoundDeleteValidator(Validator):

    def validate(self, sound):
        if sound.name in DEFAULT_DIRECTORIES + [ASTERISK_CATEGORY]:
            raise errors.not_permitted('Cannot delete default sound category')
        if sound.name in RESERVED_DIRECTORIES:
            raise errors.not_found('Sound', name=sound.name)


class SoundFileUpdateValidator(Validator):

    def validate(self, sound):
        if sound.name == ASTERISK_CATEGORY:
            raise errors.not_permitted('Cannot update system sounds')


class SoundFileDeleteValidator(Validator):

    def validate(self, sound):
        if sound.name == ASTERISK_CATEGORY:
            raise errors.not_permitted('Cannot delete system sounds')


def build_validator():
    return ValidationGroup(
        delete=[SoundDeleteValidator()],
    )


def build_validator_file():
    return ValidationGroup(
        edit=[SoundFileUpdateValidator()],
        delete=[SoundFileDeleteValidator()],
    )
