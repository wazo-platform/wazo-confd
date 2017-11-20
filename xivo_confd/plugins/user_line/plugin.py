# -*- coding: UTF-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.line import dao as line_dao

from xivo_confd import api
from xivo_confd.plugins.user_line.service import build_service
from xivo_confd.plugins.user_line.resource import UserLineList, UserLineItem, LineUserList


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(UserLineItem,
                         '/users/<int:user_id>/lines/<int:line_id>',
                         '/users/<uuid:user_id>/lines/<int:line_id>',
                         endpoint='user_lines',
                         resource_class_args=(service, user_dao, line_dao)
                         )
        api.add_resource(UserLineList,
                         '/users/<int:user_id>/lines',
                         '/users/<uuid:user_id>/lines',
                         resource_class_args=(service, user_dao, line_dao)
                         )
        api.add_resource(LineUserList,
                         '/lines/<int:line_id>/users',
                         resource_class_args=(service, user_dao, line_dao)
                         )
