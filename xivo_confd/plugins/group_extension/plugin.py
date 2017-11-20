# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd import api
from .resource import GroupExtensionItem
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(GroupExtensionItem,
                         '/groups/<int:group_id>/extensions/<int:extension_id>',
                         endpoint='group_extensions',
                         resource_class_args=(service, group_dao, extension_dao)
                         )
