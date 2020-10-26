# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.external_app import dao as external_app_dao

from wazo_confd.helpers.validator import UniqueField, ValidationGroup


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField(
                'name', lambda name: external_app_dao.find_by(name=name), 'ExternalApp'
            )
        ],
    )
