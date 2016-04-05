# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from xivo_confd.authentication.confd_auth import required_acl
from xivo_dao.helpers import errors
from xivo_confd.helpers.resource import CRUDResource
from xivo_dao.resources.func_key_template.model import UserTemplate


class TemplateManipulator(object):

    def __init__(self, tpl_service, device_updater, user_dao):
        self.tpl_service = tpl_service
        self.device_updater = device_updater
        self.user_dao = user_dao

    def update_funckey(self, template_id, position, funckey):
        template = self.tpl_service.get(template_id)
        template.keys[position] = funckey
        self.tpl_service.edit(template)

    def remove_funckey(self, template_id, position):
        template = self.tpl_service.get(template_id)
        if position in template.keys:
            del template.keys[position]
        self.tpl_service.edit(template)

    def associate_user(self, template_id, user_id):
        template = self.tpl_service.get(template_id)
        user = self.user_dao.get_by_id_uuid(user_id)
        if template.private:
            raise errors.not_permitted("Cannot associate a private template with a user",
                                       template_id=template_id)
        user.func_key_template_id = template.id
        self.user_dao.edit(user)
        self.device_updater.update_for_user(user)

    def dissociate_user(self, template_id, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        if user.func_key_template_id != template_id:
            raise errors.not_found("FuncKeyTemplate", template_id=template_id)
        user.func_key_template_id = None
        self.user_dao.edit(user)
        self.device_updater.update_for_user(user)

    def get_template(self, template_id):
        return self.tpl_service.get(template_id)

    def get_unified_template(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        if user.func_key_template_id:
            public_template = self.tpl_service.get(user.func_key_template_id)
            private_template = self.tpl_service.get(user.private_template_id)
            return public_template.merge(private_template)
        else:
            return self.tpl_service.get(user.private_template_id)

    def find_associations_by_user(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        if user.func_key_template_id:
            return [UserTemplate(user_id=user.id,
                                 template_id=user.func_key_template_id)]
        return []

    def find_associations_by_template(self, template_id):
        users = self.user_dao.find_all_by(func_key_template_id=template_id)
        return [UserTemplate(user_id=user.id,
                             template_id=user.func_key_template_id)
                for user in users]


class FuncKeyResource(object):

    def __init__(self, manipulator, fk_converter, association_converter):
        self.manipulator = manipulator
        self.fk_converter = fk_converter
        self.association_converter = association_converter

    @required_acl('confd.funckeys.templates.{template_id}.{position}.read')
    def get_funckey(self, template_id, position):
        template = self.manipulator.get_template(template_id)
        funckey = template.get(position)
        response = self.fk_converter.encode(funckey)
        return (response, 200, {'Content-Type': 'application/json'})

    @required_acl('confd.funckeys.templates.{template_id}.{position}.update')
    def update_funckey(self, template_id, position):
        funckey = self.fk_converter.decode(request)
        self.manipulator.update_funckey(template_id, position, funckey)
        return ('', 204)

    @required_acl('confd.funckeys.templates.{template_id}.{position}.delete')
    def remove_funckey(self, template_id, position):
        self.manipulator.remove_funckey(template_id, position)
        return ('', 204)

    @required_acl('confd.funckeys.templates.{template_id}.users.read')
    def get_associations(self, template_id):
        associations = self.manipulator.find_associations_by_template(template_id)
        response = self.association_converter.encode_list(associations)
        return (response, 200, {'Content-Type': 'application/json'})

    @required_acl('confd.funckeys.destinations.read')
    def get_destinations(self):
        response = self.fk_converter.description()
        return (response, 200, {'Content-Type': 'application/json'})


class FuncKeyTemplateResource(CRUDResource):

    @required_acl('confd.funckeys.templates.read')
    def search(self):
        return super(FuncKeyTemplateResource, self).search()

    @required_acl('confd.funckeys.templates.create')
    def create(self):
        return super(FuncKeyTemplateResource, self).create()

    @required_acl('confd.funckeys.templates.{resource_id}.read')
    def get(self, resource_id):
        return super(FuncKeyTemplateResource, self).get(resource_id)

    @required_acl('confd.funckeys.templates.{resource_id}.delete')
    def delete(self, resource_id):
        return super(FuncKeyTemplateResource, self).delete(resource_id)


class UserFuncKeyResource(object):

    def __init__(self, manipulator, fk_converter, association_converter, validator, user_dao):
        self.manipulator = manipulator
        self.fk_converter = fk_converter
        self.association_converter = association_converter
        self.validator = validator
        self.user_dao = user_dao

    @required_acl('confd.users.{user_id}.funckeys.{position}.update')
    def update_funckey(self, user_id, position):
        user = self.user_dao.get_by_id_uuid(user_id)
        funckey = self.fk_converter.decode(request)
        self.validator.validate(user, funckey)
        self.manipulator.update_funckey(user.private_template_id, position, funckey)
        return ('', 204)

    @required_acl('confd.users.{user_id}.funckeys.{position}.delete')
    def remove_funckey(self, user_id, position):
        user = self.user_dao.get_by_id_uuid(user_id)
        self.manipulator.remove_funckey(user.private_template_id, position)
        return ('', 204)

    @required_acl('confd.users.{user_id}.funckeys.{position}.read')
    def get_funckey(self, user_id, position):
        template = self.manipulator.get_unified_template(user_id)
        funckey = template.get(position)
        response = self.fk_converter.encode(funckey)
        return (response, 200, {'Content-Type': 'application/json'})


class UserTemplateResource(object):

    def __init__(self, manipulator, template_converter, association_converter):
        self.manipulator = manipulator
        self.template_converter = template_converter
        self.association_converter = association_converter

    @required_acl('confd.users.{user_id}.funckeys.templates.{template_id}.update')
    def associate_template(self, user_id, template_id):
        self.manipulator.associate_user(template_id, user_id)
        return ('', 204)

    @required_acl('confd.users.{user_id}.funckeys.templates.{template_id}.delete')
    def dissociate_template(self, user_id, template_id):
        self.manipulator.dissociate_user(template_id, user_id)
        return ('', 204)

    @required_acl('confd.users.{user_id}.funckeys.read')
    def get_unified_template(self, user_id):
        template = self.manipulator.get_unified_template(user_id)
        response = self.template_converter.encode(template)
        return (response, 200, {'Content-Type': 'application/json'})

    @required_acl('confd.users.{user_id}.funckeys.templates.read')
    def get_associations(self, user_id):
        associations = self.manipulator.find_associations_by_user(user_id)
        response = self.association_converter.encode_list(associations)
        return (response, 200, {'Content-Type': 'application/json'})
