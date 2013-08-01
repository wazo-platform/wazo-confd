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
from flask import Flask, request
from xivo_restapi import config

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.debug = config.DEBUG
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=5)


def register_blueprints():
    # 1.0 ressources
    from xivo_restapi.v1_0.rest import routing
    routing.create_routes()
    app.register_blueprint(routing.root)
    app.register_blueprint(routing.queues_service)
    app.register_blueprint(routing.agents_service)
    app.register_blueprint(routing.users_service)
    app.register_blueprint(routing.voicemails_service)

    # 1.1 ressources
    _load_resources()


def _load_resources():
    resources = _list_resources()
    for resource in resources:
        pkg_resource = '%s.%s' % (config.RESOURCES_PACKAGE, resource)
        _load_module('%s.routes' % pkg_resource)


def _list_resources():
    try:
        contents = pkg_resources.resource_listdir(config.RESOURCES_PACKAGE, "")
    except ImportError:
        return []
    resources = []
    for entry in contents:
        if not entry.endswith('.py') and not entry.endswith('.pyc'):
            if pkg_resources.resource_isdir(config.RESOURCES_PACKAGE, entry):
                logger.debug('Resources found: %s', entry)
                resources.append(entry)
    return resources


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
        logger.debug('Module successfully loaded: %s', name)


@app.before_request
def log_requests():
    app.config['SERVER_NAME'] = request.environ['HTTP_HOST']
    params = {
        'method': request.method,
        'path': request.path
    }
    if request.data:
        params.update({'data': request.data})
        logger.info("%(method)s %(path)s with data %(data)s", params)
    else:
        logger.info("%(method)s %(path)s", params)
