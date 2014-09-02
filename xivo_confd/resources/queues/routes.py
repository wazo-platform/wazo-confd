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
from flask.blueprints import Blueprint

from xivo_confd import config
from xivo_confd.helpers.route_generator import RouteGenerator


blueprint = Blueprint('queues', __name__, url_prefix='/%s/queues' % config.VERSION_1_1)
queue_route = RouteGenerator(blueprint)


def register_blueprints(app):
    app.register_blueprint(blueprint)
