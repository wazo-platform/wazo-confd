# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao


class UserEntityService(object):

    def __init__(self, dao):
        self.dao = dao

    def find_by(self, **criteria):
        user_id = criteria.pop('user_id', None)
        if user_id:
            criteria['id'] = user_id
        user = self.dao.find_by(**criteria)
        if user:
            user.user_id = user_id
        return user

    def associate(self, user, entity):
        user.entity_id = entity.id
        self.dao.edit(user)


def build_service():
    return UserEntityService(user_dao)
