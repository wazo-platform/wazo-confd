# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.moh import dao as moh_dao

from wazo_confd.helpers.validator import UniqueField, Validator, ValidationGroup


class MohModelValidator(Validator):
    def validate(self, moh):
        if moh.mode == 'custom' and moh.application is None:
            raise errors.moh_custom_no_app()


def build_validator():
    moh_validator = MohModelValidator()

    return ValidationGroup(
        create=[
            UniqueField('name', lambda name: moh_dao.find_by(name=name), 'MOH'),
            moh_validator,
        ],
        edit=[moh_validator],
    )
