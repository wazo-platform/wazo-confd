# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.outcall import dao as outcall_dao
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd import api
from .resource import OutcallExtensionItem
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(OutcallExtensionItem,
                         '/outcalls/<int:outcall_id>/extensions/<int:extension_id>',
                         endpoint='outcall_extensions',
                         resource_class_args=(service, outcall_dao, extension_dao)
                         )
