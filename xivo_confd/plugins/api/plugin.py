# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api

from xivo_confd.plugins.api.resource import SwaggerResource


class Plugin(object):

    def load(self, core):
        api.add_resource(SwaggerResource,
                         '/api/api.yml',
                         resource_class_args=(core.config,))
