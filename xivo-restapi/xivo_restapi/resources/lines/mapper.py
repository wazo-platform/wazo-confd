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
    'name': 'name',
}


def encode_list(lines, include=[]):
    mapped_lines = [map_line(line, include) for line in lines]
    return mapper.encode_list(mapped_lines)


def encode_line(line, include=[]):
    mapped_line = map_line(line, include)
    return mapper.encode(mapped_line)


def map_line(line, include=[]):
    data = mapper.map_entity(MAPPING, line)

    return data
