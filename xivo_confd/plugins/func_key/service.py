# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

from xivo_confd.plugins.func_key.validator import build_validator, build_validator_bsfilter
from xivo_confd.plugins.func_key.notifier import build_notifier
from xivo_confd.plugins.device import builder as device_builder

from xivo_dao.resources.func_key_template.model import UserTemplate

from xivo_dao.resources.func_key_template import dao as template_dao
from xivo_dao.resources.user import dao as user_dao

from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers import errors


class TemplateService(object):

    DESTINATION_BLFS = ('user',
                        'conference',
                        'custom',
                        'bsfilter',
                        'forward',
                        'agent',
                        'park_position')

    SERVICE_BLFS = ('callrecord',
                    'incallfilter',
                    'enablednd',
                    'enablevm')

    def __init__(self, template_dao, user_dao, validator, validator_bsfilter, notifier, device_updater):
        self.template_dao = template_dao
        self.user_dao = user_dao
        self.validator = validator
        self.notifier = notifier
        self.device_updater = device_updater
        self.validator_bsfilter = validator_bsfilter

    def get(self, template_id):
        return self.template_dao.get(template_id)

    def get_unified_template(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        if user.func_key_template_id:
            public_template = self.get(user.func_key_template_id)
            private_template = self.get(user.private_template_id)
            return public_template.merge(private_template)
        else:
            return self.get(user.private_template_id)

    def search(self, parameters):
        return self.template_dao.search(**parameters)

    def create(self, template):
        self.validator.validate_create(template)
        self._adjust_blfs(template)
        created_template = self.template_dao.create(template)
        self.notifier.created(created_template)
        return created_template

    def edit(self, template, updated_fields=None):
        self.validator.validate_edit(template)
        self._adjust_blfs(template)
        self.template_dao.edit(template)
        self.device_updater.update_for_template(template)
        self.notifier.edited(template, updated_fields)

    def edit_funckey(self, funckey, template, position):
        template.keys[position] = funckey
        updated_fields = [position]
        self.edit(template, updated_fields)

    def edit_user_funckey(self, user, funckey, template, position):
        self.validator_bsfilter.validate(user, funckey)
        self.edit_funckey(funckey, template, position)

    def edit_user_template(self, user, template, updated_fields):
        for funckey in template.keys.itervalues():
            self.validator_bsfilter.validate(user, funckey)
        self.edit(template, updated_fields)

    def delete(self, template):
        self.validator.validate_delete(template)
        users = self.user_dao.find_all_by(func_key_template_id=template.id)
        self.template_dao.delete(template)
        for user in users:
            Session.expire(user, ['func_key_template_id'])
            self.device_updater.update_for_user(user)
        self.notifier.deleted(template)

    def delete_funckey(self, template, position):
        if position in template.keys:
            del template.keys[position]
        updated_fields = [position]
        self.edit(template, updated_fields)

    def _adjust_blfs(self, template):
        for funckey in template.keys.values():
            destination = funckey.destination
            if destination.type == 'service':
                if destination.service not in self.SERVICE_BLFS:
                    funckey.blf = False
            elif destination.type not in self.DESTINATION_BLFS:
                funckey.blf = False


def build_service(provd_client):
    device_updater = device_builder.build_device_updater(provd_client)

    return TemplateService(template_dao,
                           user_dao,
                           build_validator(),
                           build_validator_bsfilter(),
                           build_notifier(),
                           device_updater)


class UserFuncKeyTemplateService(object):

    def __init__(self, user_dao, validator, notifier, device_updater):
        self.user_dao = user_dao
        self.validator = validator
        self.notifier = notifier
        self.device_updater = device_updater

    def find_all_by_template_id(self, template_id):
        users = self.user_dao.find_all_by(func_key_template_id=template_id)
        return [UserTemplate(user_id=user.id, template_id=user.func_key_template_id) for user in users]

    def find_all_by_user_id(self, user_id):
        user = self.user_dao.get(user_id=user_id)
        if user.func_key_template_id:
            return [UserTemplate(user_id=user.id,
                                 template_id=user.func_key_template_id)]
        return []

    def associate(self, user, template):
        if template.private:
            raise errors.not_permitted("Cannot associate a private template with a user",
                                       template_id=template.id)

        user.func_key_template_id = template.id
        self.user_dao.edit(user)
        self.device_updater.update_for_user(user)

    def dissociate(self, user, template):
        if user.func_key_template_id != template.id:
            raise errors.not_found("FuncKeyTemplate",
                                   template_id=template.id)

        user.func_key_template_id = None
        self.user_dao.edit(user)
        self.device_updater.update_for_user(user)


def build_user_funckey_template_service(provd_client):
    device_updater = device_builder.build_device_updater(provd_client)

    return UserFuncKeyTemplateService(user_dao,
                                      build_validator(),
                                      build_notifier(),
                                      device_updater)
