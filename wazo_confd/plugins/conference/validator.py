# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.moh import dao as moh_dao

from wazo_confd.helpers.validator import MOHExists, ValidationGroup


def build_validator():
    moh_validator = MOHExists('music_on_hold', moh_dao.get_by)
    return ValidationGroup(create=[moh_validator], edit=[moh_validator])
