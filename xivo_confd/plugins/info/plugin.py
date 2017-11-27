# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api

from .service import build_service
from .resource import Info


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(
            Info,
            '/infos',
            resource_class_args=(service,)
        )
