# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao

from xivo_confd import api
from .resource import UserFallbackList
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(UserFallbackList,
                         '/users/<uuid:user_id>/fallbacks',
                         '/users/<int:user_id>/fallbacks',
                         resource_class_args=(service, user_dao)
                         )
