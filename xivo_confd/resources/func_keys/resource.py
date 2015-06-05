# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from flask import request

from xivo_dao.helpers import errors


class FuncKeyResource(object):

    def __init__(self, service, converter):
        self.service = service
        self.converter = converter

    def get_funckey(self, template_id, position):
        template = self.service.get(template_id)
        if position not in template.keys:
            raise errors.not_found('FuncKey', template_id=template_id, position=position)
        funckey = template.keys[position]
        response = self.converter.encode(funckey)
        return (response, 200, {'Content-Type': 'application/json'})

    def update_funckey(self, template_id, position):
        template = self.service.get(template_id)
        funckey = self.converter.decode(request)
        template.keys[position] = funckey
        self.service.edit(template)
        return ('', 204)

    def remove_funckey(self, template_id, position):
        template = self.service.get(template_id)
        if position in template.keys:
            del template.keys[position]
        self.service.edit(template)
        return ('', 204)
