# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

import logging
import os
import pkg_resources

from datetime import timedelta
from flask import Flask
from xivo_restapi import config

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.debug = config.DEBUG
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=5)


def register_blueprints():
    from xivo_restapi.v1_0.rest import routing
    routing.create_routes()
    app.register_blueprint(routing.root)
    app.register_blueprint(routing.queues_service)
    app.register_blueprint(routing.agents_service)
    app.register_blueprint(routing.users_service)
    app.register_blueprint(routing.voicemails_service)

    _load_ressources()


def _list_ressources():
    try:
        contents = pkg_resources.resource_listdir(config.RESSOURCES_PACKAGE, "")
    except ImportError:
        return []
    ressources = []
    for entry in contents:
        if not entry.endswith('.py') and  not entry.endswith('.pyc'):
            if pkg_resources.resource_isdir(config.RESSOURCES_PACKAGE, entry):
                logger.debug('Ressources found: %s', entry)
                ressources.append(entry)
    return ressources


def _load_ressources():
    ressources = _list_ressources()
    for ressource in ressources:
        pkg_ressource = '%s.%s' % (config.RESSOURCES_PACKAGE, ressource)
        _load_module('%s.routes' % pkg_ressource)


def _load_module(name):
    try:
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
    except ImportError:
        logger.error('Module not found %s', name)
    else:
        mod.register_blueprints(app)


class FlaskHttpServer(object):

    def run(self):
        app.run(host=config.HOST, port=config.PORT)
