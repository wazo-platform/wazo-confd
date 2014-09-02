# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from xivo_dao.data_handler.user import services as user_services
from xivo_dao.data_handler.line import services as line_services
from xivo_dao.data_handler.extension import services as extension_services

#Each of these methods wil raise a NotFoundError if the resource doesn't exist


def check_user_exists(user_id):
    return user_services.get(user_id)


def check_line_exists(line_id):
    return line_services.get(line_id)


def check_extension_exists(extension_id):
    return extension_services.get(extension_id)
