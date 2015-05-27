# -*- coding: UTF-8 -*-

# Copyright (C) 2013-2015 Avencall
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


class TemplateService(object):

    def __init__(self, validator, template_dao, user_dao, notifier, device_updater):
        self.validator = validator
        self.template_dao = template_dao
        self.user_dao = user_dao
        self.notifier = notifier
        self.device_updater = device_updater

    def get(self, template_id):
        return self.template_dao.get(template_id)

    def create(self, template):
        self.validator.validate_create(template)
        created_template = self.template_dao.create(template)
        self.notifier.created(created_template)
        return created_template

    def edit(self, template):
        self.validator.validate_edit(template)
        self.template_dao.edit(template)
        self.device_updater.update_for_template(template)
        self.notifier.edited(template)

    def delete(self, template):
        self.validator.validate_delete(template)
        users = self.user_dao.find_all_by_template_id(template.id)
        self.template_dao.delete(template)
        self.device_updater.update_for_users(users)
        self.notifier.deleted(template)


class DeviceUpdater(object):

    def update_for_template(self, template):
        pass

    def update_for_users(self, users):
        pass
