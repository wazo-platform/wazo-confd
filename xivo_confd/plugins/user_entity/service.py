# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao

from xivo_confd.plugins.user_entity.notifier import build_notifier
from xivo_confd.plugins.user_entity.validator import build_validator


class UserEntityService(object):

    def __init__(self, dao, validator, notifier):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier

    def find_by(self, **criteria):
        user_id = criteria.pop('user_id', None)
        if user_id:
            criteria['id'] = user_id
        user = self.dao.find_by(**criteria)
        if user:
            user.user_id = user_id
        return user

    def associate(self, user, entity):
        self.validator.validate_association(user, entity)
        user.entity_id = entity.id
        self.dao.edit(user)
        self.notifier.associated(user, entity)


def build_service():
    return UserEntityService(user_dao,
                             build_validator(),
                             build_notifier())
