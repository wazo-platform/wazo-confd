# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_provd_client import new_provisioning_client_from_config

logger = logging.getLogger(__name__)


class CoreRestApi(object):

    def __init__(self, app, api, auth):
        self.app = app
        self.api = api
        self.auth = auth

    @property
    def config(self):
        return self.app.config

    def blueprint(self, name):
        return self.app.blueprints[name]

    def register(self, blueprint):
        self.app.register_blueprint(blueprint)

    def provd_client(self):
        return new_provisioning_client_from_config(self.config['provd'])
