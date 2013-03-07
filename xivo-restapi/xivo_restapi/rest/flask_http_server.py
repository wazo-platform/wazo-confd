# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

from datetime import timedelta
from flask import Flask
from xivo_restapi.rest.routage import root, queues_service, agents_service, \
    users_service
from xivo_restapi.restapi_config import RestAPIConfig
import logging
import os

logger = logging.getLogger(__name__)

app = Flask(__name__)

app.register_blueprint(root)
app.register_blueprint(queues_service)
app.register_blueprint(agents_service)
app.register_blueprint(users_service)
app.debug = True
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=1)


class FlaskHttpServer(object):

    def run(self):
        app.run(host="0.0.0.0",
                port=RestAPIConfig.XIVO_RECORD_SERVICE_PORT)
