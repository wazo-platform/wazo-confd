# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao

from .notifier import build_notifier
from .validator import build_validator


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
        if user.entity_id == entity.id:
            return

        self.validator.validate_association(user, entity)
        user.entity_id = entity.id
        self.dao.edit(user)
        self.notifier.associated(user, entity)


def build_service():
    return UserEntityService(user_dao,
                             build_validator(),
                             build_notifier())
