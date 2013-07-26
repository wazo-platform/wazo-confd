# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_restapi.helpers import mapper

# mapping = {db_field: model_field}
MAPPING = {
    'id': 'id',
    'exten': 'exten',
    'context': 'context',
    'commented': 'commented'
}


def encode_list(extensions, include=[]):
    mapped_extensions = [map_extension(extension, include) for extension in extensions]
    return mapper.encode_list(mapped_extensions)


def encode_extension(extension, include=[]):
    mapped_extension = map_extension(extension, include)
    return mapper.encode(mapped_extension)


def map_extension(extension, include=[]):
    data = mapper.map_entity(MAPPING, extension)

    return data
