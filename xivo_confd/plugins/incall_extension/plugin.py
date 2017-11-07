# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd import api
from .resource import IncallExtensionItem
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(IncallExtensionItem,
                         '/incalls/<int:incall_id>/extensions/<int:extension_id>',
                         endpoint='incall_extensions',
                         resource_class_args=(service, incall_dao, extension_dao)
                         )
