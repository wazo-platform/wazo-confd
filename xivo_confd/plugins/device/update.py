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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


class DeviceUpdater(object):

    def __init__(self, user_dao, line_dao, user_line_dao, line_extension_dao, func_key_template_db, provd_updater):
        self.user_dao = user_dao
        self.line_dao = line_dao
        self.user_line_dao = user_line_dao
        self.line_extension_dao = line_extension_dao
        self.func_key_template_db = func_key_template_db
        self.provd_updater = provd_updater

    def update_for_template(self, template):
        private_users = self.user_dao.find_all_by(func_key_private_template_id=template.id)
        public_users = self.user_dao.find_all_by(func_key_template_id=template.id)
        for user in private_users + public_users:
            self.update_for_user(user)

    def update_for_extension(self, extension):
        line_extensions = self.line_extension_dao.find_all_by(extension_id=extension.id)
        for line_extension in line_extensions:
            line = self.line_dao.get(line_extension.line_id)
            self.update_for_line(line)

        func_key_templates = self._find_all_fk_templates_by_extension(extension)
        for func_key_template in func_key_templates:
            self.update_for_template(func_key_template)

    def _find_all_fk_templates_by_extension(self, extension):
        user_id = self._find_user_id_by_extension(extension)
        if user_id:
            return self.func_key_template_db.find_all_dst_user(user_id)
        return []

    def _find_user_id_by_extension(self, extension):
        line_extension = self.line_extension_dao.find_by(extension_id=extension.id)
        if line_extension:
            user_line = self.user_line_dao.find_by(line_id=line_extension.line_id, main_user=True)
            return user_line.user_id

    def update_for_user(self, user):
        for user_line in self.user_line_dao.find_all_by_user_id(user.id):
            line = self.line_dao.get(user_line.line_id)
            self.update_for_line(line)

    def update_for_endpoint_sip(self, sip):
        line = self.line_dao.find_by(protocol='sip', protocolid=sip.id)
        if line:
            self.update_for_line(line)

    def update_for_line(self, line):
        if line.device_id:
            self.provd_updater.update(line.device_id)

    def update_device(self, device):
        self.provd_updater.update(device.id)


class ProvdUpdater(object):

    def __init__(self, dao, config_generator, line_dao):
        self.dao = dao
        self.config_generator = config_generator
        self.line_dao = line_dao

    def update(self, device_id):
        device = self.dao.get(device_id)
        has_lines = self.device_has_lines(device)

        if device.is_autoprov() and has_lines:
            self.create_device(device)
        elif has_lines:
            self.update_device(device)
        else:
            self.reset_autoprov(device)

    def device_has_lines(self, device):
        lines = self.line_dao.find_all_by(device_id=device.id)
        return len(lines) > 0

    def create_device(self, device):
        config = self.config_generator.generate(device)
        device.update_config(config)
        self.dao.create_or_update(device)

    def update_device(self, device):
        config = self.config_generator.generate(device)
        device.update_config(config)
        self.dao.edit(device)

    def reset_autoprov(self, device):
        self.dao.reset_autoprov(device)
