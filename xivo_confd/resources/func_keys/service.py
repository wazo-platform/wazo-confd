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
        self.adjust_blfs(template)
        created_template = self.template_dao.create(template)
        self.notifier.created(created_template)
        return created_template

    def edit(self, template):
        self.validator.validate_edit(template)
        self.adjust_blfs(template)
        self.template_dao.edit(template)
        self.device_updater.update_for_template(template)
        self.notifier.edited(template)

    def delete(self, template):
        self.validator.validate_delete(template)
        users = self.user_dao.find_all_by_template_id(template.id)
        self.template_dao.delete(template)
        for user in users:
            self.device_updater.update_for_user(user)
        self.notifier.deleted(template)

    def adjust_blfs(self, template):
        for funckey in template.keys.values():
            destination = funckey.destination
            if destination.type == 'service':
                if destination.service not in self.SERVICE_BLFS:
                    funckey.blf = False
            elif destination.type not in self.DESTINATION_BLFS:
                funckey.blf = False
