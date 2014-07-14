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

from document import Document, DocumentProxy
from errors import ContentTypeError


class Parser(object):

    def __init__(self, registry):
        self.registry = registry
        self.error_handler_callback = self._default_error_handler

    def _default_error_handler(self, error):
        raise error

    def parse(self, request, document, action=None):
        try:
            content, content_type = self._extract_from_request(request)
            content = self.registry.parse(content, content_type, document)
            document.validate(content, action)
            return content
        except Exception as e:
            self.error_handler_callback(e)

    def _extract_from_request(self, request):
        content_type = request.headers.get('Content-Type')
        content = request.data

        if not content_type:
            raise ContentTypeError('Content-Type required')

        return content, content_type

    def document(self, *fields):
        document = Document(fields)
        return DocumentProxy(self, document)

    def error_handler(self, func):
        self.error_handler_callback = func
        return func

    def content_parser(self, content_type):
        def wrapper(func):
            self.registry.register(content_type, func)
            return func
        return wrapper
