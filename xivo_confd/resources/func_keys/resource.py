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


class TemplateManipulator(object):

    def __init__(self, service):
        self.service = service

    def get_funckey(self, template_id, position):
        template = self.service.get(template_id)
        if position not in template.keys:
            raise errors.not_found('FuncKey', template_id=template_id, position=position)
        return template.keys[position]

    def update_funckey(self, template_id, position, funckey):
        template = self.service.get(template_id)
        template.keys[position] = funckey
        self.service.edit(template)

    def remove_funckey(self, template_id, position):
        template = self.service.get(template_id)
        if position in template.keys:
            del template.keys[position]
        self.service.edit(template)


class FuncKeyResource(object):

    def __init__(self, manipulator, converter):
        self.manipulator = manipulator
        self.converter = converter

    def get_funckey(self, template_id, position):
        funckey = self.manipulator.get_funckey(template_id, position)
        response = self.converter.encode(funckey)
        return (response, 200, {'Content-Type': 'application/json'})

    def update_funckey(self, template_id, position):
        funckey = self.converter.decode(request)
        self.manipulator.update_funckey(template_id, position, funckey)
        return ('', 204)

    def remove_funckey(self, template_id, position):
        self.manipulator.remove_funckey(template_id, position)
        return ('', 204)


class UserFuncKeyResource(object):

    def __init__(self, manipulator, converter, validator, user_dao):
        self.manipulator = manipulator
        self.converter = converter
        self.validator = validator
        self.user_dao = user_dao

    def update_funckey(self, user_id, position):
        user = self.user_dao.get(user_id)
        funckey = self.converter.decode(request)
        self.validator.validate(user, funckey)
        self.manipulator.update_funckey(user.private_template_id, position, funckey)
        return ('', 204)

    def remove_funckey(self, user_id, position):
        user = self.user_dao.get(user_id)
        self.manipulator.remove_funckey(user.private_template_id, position)
        return ('', 204)

    def get_funckey(self, user_id, position):
        user = self.user_dao.get(user_id)
        funckey = self.manipulator.get_funckey(user.private_template_id, position)
        response = self.converter.encode(funckey)
        return (response, 200, {'Content-Type': 'application/json'})


class UserTemplateResource(object):

    def __init__(self, user_dao, template_dao, template_converter):
        self.user_dao = user_dao
        self.template_dao = template_dao
        self.template_converter = template_converter

    def associate_template(self, user_id, template_id):
        template = self.template_dao.get(template_id)
        user = self.user_dao.get(user_id)
        if template.private:
            raise errors.not_permitted("Cannot associate a private template with a user",
                                       template_id=template_id)
        user.func_key_template_id = template.id
        self.user_dao.edit(user)
        return ('', 204)

    def dissociate_template(self, user_id, template_id):
        self.template_dao.get(template_id)
        user = self.user_dao.get(user_id)
        if user.func_key_template_id != template_id:
            raise errors.not_found("FuncKeyTemplate", template_id=template_id)
        user.func_key_template_id = None
        self.user_dao.edit(user)
        return ('', 204)

    def get_unified_template(self, user_id):
        user = self.user_dao.get(user_id)
        if user.func_key_template_id:
            public_template = self.template_dao.get(user.func_key_template_id)
            private_template = self.template_dao.get(user.private_template_id)
            unified_template = public_template.merge(private_template)
        else:
            unified_template = self.template_dao.get(user.private_template_id)
        response = self.template_converter.encode(unified_template)
        return (response, 200, {'Content-Type': 'application/json'})
