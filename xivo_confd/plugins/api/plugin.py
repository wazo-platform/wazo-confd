# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api

from .resource import SwaggerResource


class Plugin(object):

    def load(self, core):
        api.add_resource(
            SwaggerResource,
            '/api/api.yml',
            resource_class_args=(core.config,)
        )
