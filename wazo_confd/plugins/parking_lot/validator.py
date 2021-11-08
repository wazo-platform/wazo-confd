# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.moh import dao as moh_dao

from wazo_confd.helpers.validator import MOHExists, ValidationGroup, Validator


class SlotsAvailableValidator(Validator):
    def validate(self, parking_lot):
        if not parking_lot.extensions:
            return

        extensions = extension_dao.find_all_by(
            context=parking_lot.extensions[0].context
        )
        for extension in extensions:
            if extension.is_pattern():
                continue
            if parking_lot.in_slots_range(extension.exten):
                raise errors.resource_exists(
                    'Extension',
                    id=extension.id,
                    exten=extension.exten,
                    context=extension.context,
                )


def build_validator():
    moh_validator = MOHExists('music_on_hold', moh_dao.get_by)
    return ValidationGroup(
        create=[moh_validator], edit=[SlotsAvailableValidator(), moh_validator],
    )
