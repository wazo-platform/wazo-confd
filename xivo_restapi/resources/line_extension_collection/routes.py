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

from flask import request, url_for, make_response

from . import actions
from xivo_restapi.resources.lines.routes import line_blueprint, line_route


@line_route('/<int:lineid>/extensions')
def list_extensions(lineid):
    response = actions.list_extensions(lineid)
    return make_response(response, 200)


@line_route('/<int:lineid>/extensions', methods=['POST'])
def associate_line_extension(lineid):
    parameters = request.data.decode("utf-8")
    response = actions.associate_extension(lineid, parameters)
    location = url_for('.list_extensions', lineid=lineid)
    return make_response(response, 201, {'Location': location})


def register_blueprints(app):
    app.register_blueprint(line_blueprint)
