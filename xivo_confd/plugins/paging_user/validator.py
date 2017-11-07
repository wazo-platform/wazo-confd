# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class PagingUserAssociationValidator(ValidatorAssociation):

    def validate(self, paging, users):
        self.validate_no_duplicate_user(users)

    def validate_no_duplicate_user(self, users):
        if len(users) != len(set(users)):
            raise errors.not_permitted('Cannot associate same user more than once')


def build_validator():
    return ValidationAssociation(
        association=[PagingUserAssociationValidator()],
    )
