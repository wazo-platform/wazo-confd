# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_confd import bus, sysconfd

from .notifier import HANotifier
from .resource import HAResource
from .service import HAService


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        notifier = HANotifier(bus, sysconfd)
        service = HAService(notifier, sysconfd)

        api.add_resource(
            HAResource,
            '/ha',
            resource_class_args=(service,)
        )
