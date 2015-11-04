# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging

from xivo_confd.helpers.mooltiparse import parser as mooltiparse_parser

from xivo_provd_client import new_provisioning_client_from_config

logger = logging.getLogger(__name__)


class CoreRestApi(object):

    def __init__(self, app, api, auth):
        self.app = app
        self.api = api
        self.auth = auth
        self.content_parser = mooltiparse_parser()

    @property
    def config(self):
        return self.app.config

    def blueprint(self, name):
        return self.app.blueprints[name]

    def register(self, blueprint):
        self.app.register_blueprint(blueprint)

    def provd_client(self):
        return new_provisioning_client_from_config(self.config['provd'])
