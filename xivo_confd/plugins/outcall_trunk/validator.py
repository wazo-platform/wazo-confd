# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class GroupTrunkAssociationValidator(ValidatorAssociation):

    def validate(self, group, trunks):
        self.validate_no_duplicate_trunk(trunks)

    def validate_no_duplicate_trunk(self, trunks):
        if len(trunks) != len(set(trunks)):
            raise errors.not_permitted('Cannot associate same trunk more than once')


def build_validator():
    return ValidationAssociation(
        association=[GroupTrunkAssociationValidator()],
    )
