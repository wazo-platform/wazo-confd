# -*- coding: utf-8 -*-
#
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.user import dao as user_dao

from xivo_confd import api
from .resource import UserGroupItem
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(UserGroupItem,
                         '/users/<uuid:user_id>/groups',
                         '/users/<int:user_id>/groups',
                         endpoint='user_groups',
                         resource_class_args=(service, user_dao, group_dao)
                         )
