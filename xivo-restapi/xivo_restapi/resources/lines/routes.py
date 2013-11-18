# -*- coding: utf-8 -*-
#
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import Blueprint

from xivo_restapi import config
from xivo_restapi.helpers.route_generator import RouteGenerator
from xivo_restapi.resources.lines.actions_sip import blueprint as line_sip_blueprint

line_blueprint = Blueprint('lines', __name__, url_prefix='/%s/lines' % config.VERSION_1_1)
line_route = RouteGenerator(line_blueprint)

from xivo_restapi.resources.lines import actions


def register_blueprints(app):
    app.register_blueprint(line_blueprint)
    app.register_blueprint(line_sip_blueprint)
