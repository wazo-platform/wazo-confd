# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.group import dao as group_dao

from xivo_confd import api
from .resource import GroupFallbackList
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(
            GroupFallbackList,
            '/groups/<int:group_id>/fallbacks',
            resource_class_args=(service, group_dao)
        )
