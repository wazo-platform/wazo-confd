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

from xivo_dao.data_handler.line_extension import services as line_extension_services

from xivo_restapi.helpers import url
from xivo_restapi.resources.line_extension_collection.formatter import LineExtensionFormatter

formatter = LineExtensionFormatter()


def associate_extension(line_id, parameters):
    url.check_line_exists(line_id)
    model = formatter.dict_to_model(line_id, parameters)
    created_model = line_extension_services.associate(model)
    return formatter.to_api(created_model)


def dissociate_extension(line_id, extension_id):
    url.check_line_exists(line_id)
    url.check_extension_exists(extension_id)
    model = formatter.model_from_ids(line_id, extension_id)
    line_extension_services.dissociate(model)
    return ''


def list_extensions(line_id):
    url.check_line_exists(line_id)
    line_extensions = line_extension_services.get_all_by_line_id(line_id)
    return formatter.list_to_api(line_extensions)
