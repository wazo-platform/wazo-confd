# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.plugins.extension.service import build_service
from xivo_confd.plugins.extension.resource import ExtensionItem, ExtensionList


class Plugin(object):

    def load(self, core):
        api = core.api

        provd_client = core.provd_client()

        service = build_service(provd_client)

        api.add_resource(ExtensionItem,
                         '/extensions/<int:id>',
                         endpoint='extensions',
                         resource_class_args=(service,)
                         )
        api.add_resource(ExtensionList,
                         '/extensions',
                         resource_class_args=(service,)
                         )
