# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_confd import api
from xivo_confd.plugins.user_line_associated.resource import UserLineAssociatedEndpointSipItem


class Plugin(object):

    def load(self, core):
        api.add_resource(UserLineAssociatedEndpointSipItem,
                         '/users/<uuid:user_uuid>/lines/<line_id>/associated/endpoints/sip',
                         resource_class_args=(user_dao, line_dao)
                         )
