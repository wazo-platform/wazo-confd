# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.context import dao as context_dao

from .resource import ContextContextList
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service(context_dao)

        api.add_resource(
            ContextContextList,
            '/contexts/<int:context_id>/contexts',
            resource_class_args=(service, context_dao)
        )
