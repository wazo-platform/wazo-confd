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

import logging

from flask import Blueprint
from xivo_restapi.ressources.users import api
from xivo_restapi import config

logger = logging.getLogger(__name__)

root_1_1 = Blueprint("root_users_%s" % config.VERSION_1_1,
                     __name__,
                     url_prefix='/%s/users' % config.VERSION_1_1)

root_1_1.add_url_rule("/",
                      "list",
                      api.list,
                      methods=["GET"])

root_1_1.add_url_rule("/<int:userid>",
                      "get",
                      api.get,
                      methods=["GET"])

root_1_1.add_url_rule("/",
                      "create",
                      api.create,
                      methods=["POST"])

root_1_1.add_url_rule("/<int:userid>",
                      "edit",
                      api.edit,
                      methods=["PUT"])

root_1_1.add_url_rule("/<int:userid>",
                      "delete",
                      api.delete,
                      methods=["DELETE"])


def register_blueprints(app):
    app.register_blueprint(root_1_1)
