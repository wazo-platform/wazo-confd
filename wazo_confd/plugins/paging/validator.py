# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.paging import dao as paging_dao

from wazo_confd.helpers.validator import (
    Optional,
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('number', lambda number: paging_dao.find_by(number=number), 'Paging'),
        ],
        edit=[
            Optional('number', UniqueFieldChanged('number', paging_dao, 'Paging')),
        ]
    )
