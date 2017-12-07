# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.validator import ValidationAssociation, ValidatorAssociation
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.helpers import errors


class UserEntityAssociationValidator(ValidatorAssociation):

    def __init__(self, user_line_dao):
        self.user_line_dao = user_line_dao

    def validate(self, user, entity):
        if user.entity_id == entity.id:
            return
        self.validate_user_no_line_associated(user)

    def validate_user_no_line_associated(self, user):
        user_lines = self.user_line_dao.find_all_by(user_id=user.id)
        if user_lines:
            line_ids = ','.join(str(ul.line_id) for ul in user_lines)
            raise errors.resource_associated('User', 'Line',
                                             user_id=user.id,
                                             line_ids=line_ids)


def build_validator():
    return ValidationAssociation(
        association=[
            UserEntityAssociationValidator(user_line_dao)
        ]
    )
