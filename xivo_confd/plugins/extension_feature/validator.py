# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd.helpers.validator import Validator, ValidationGroup


class ExtenAvailableOnUpdateValidator(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, extension):
        existing = self.dao.find_by(exten=extension.exten,
                                    context=extension.context)
        if existing and existing.id != extension.id:
            raise errors.resource_exists('Extension',
                                         exten=extension.exten,
                                         context=extension.context)


def build_validator():
    return ValidationGroup(
        edit=[
            ExtenAvailableOnUpdateValidator(extension_dao),
        ],
    )
