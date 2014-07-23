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

from errors import ContentTypeError


class ParserRegistry(object):

    def __init__(self):
        self.parsers = {}

    def parser_for_content_type(self, content_type):
        parser = self.parsers.get(content_type)
        if not parser:
            supported = ', '.join(self.parsers.keys())
            msg = 'Supported Content-Types: {}'.format(supported)
            raise ContentTypeError(msg)
        return parser

    def register(self, content_type, parser):
        self.parsers[content_type] = parser
