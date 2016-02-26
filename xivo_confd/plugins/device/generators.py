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


class ConfigGenerator(object):

    def __init__(self, generators):
        self.generators = generators

    def generate(self, device):
        configdevice = device.extract_config_device()
        config = {'id': device.id,
                  'configdevice': configdevice,
                  'parent_ids': ['base', configdevice],
                  'X_key': '',
                  'config_version': 1}

        for generator in self.generators:
            section = generator.generate(device)
            if section:
                config.update(section)
        return config


class RawConfigGenerator(object):

    def __init__(self, generators):
        self.generators = generators

    def generate(self, device):
        raw_config = {}
        for generator in self.generators:
            section = generator.generate(device)
            if section:
                raw_config.update(section)
        return {'raw_config': raw_config}


class FuncKeyGenerator(object):

    def __init__(self, user_dao, line_dao, user_line_dao, template_dao, device_dao, converters):
        self.user_dao = user_dao
        self.line_dao = line_dao
        self.user_line_dao = user_line_dao
        self.device_dao = device_dao
        self.template_dao = template_dao
        self.converters = converters

    def generate(self, device):
        user, line = self.user_line_for_device(device.id)
        if user and line:
            template = self.get_unified_template(user)
            funckeys = self.convert_funckeys(user, line, template)
            return {'funckeys': funckeys}

    def user_line_for_device(self, device_id):
        line = self.line_dao.find_by(device=device_id, device_slot=1)
        main_user_line = self.user_line_dao.find_main_user_line(line.id)
        if main_user_line:
            user = self.user_dao.get(main_user_line.user_id)
            return user, line
        return None, None

    def get_unified_template(self, user):
        private_template = self.template_dao.get(user.private_template_id)
        if user.func_key_template_id:
            public_template = self.template_dao.get(user.func_key_template_id)
            return public_template.merge(private_template)
        return private_template

    def convert_funckeys(self, user, line, template):
        funckeys = {}
        for pos, funckey in template.keys.iteritems():
            converter = self.converters[funckey.destination.type]
            funckeys.update(converter.build(user, line, pos, funckey))
        return funckeys


class SipGenerator(object):

    def __init__(self, device_dao, device_db):
        self.device_dao = device_dao
        self.device_db = device_db

    def generate(self, device):
        section = {}
        rows = self.device_db.sip_lines_for_device(device.id)
        for row in rows:
            slot = row.LineFeatures.device_slot
            config = self.generate_config(row)
            section[slot] = config

        if len(section) > 0:
            return {'sip_lines': section}

    def generate_config(self, row):
        line = row.LineFeatures
        sip = row.UserSIP
        extension = row.Extension
        registrar = self.device_dao.get_registrar(line.configregistrar)

        config = {'auth_username': sip.name,
                  'username': sip.name,
                  'password': sip.secret,
                  'display_name': line.caller_id_name,
                  'number': extension.exten,
                  'registrar_ip': registrar['registrar_main'],
                  'proxy_ip': registrar['proxy_main']}

        proxy_backup = registrar.get('proxy_backup', '')
        if proxy_backup:
            config['backup_proxy_ip'] = proxy_backup
            config['backup_registrar_ip'] = registrar['registrar_backup']

        return config


class SccpGenerator(object):

    def __init__(self, device_dao, line_dao):
        self.device_dao = device_dao
        self.line_dao = line_dao

    def generate(self, device):
        section = {}
        line = self.line_dao.find_by(device=device.id)
        if line:
            registrar = self.device_dao.get_registrar(line.configregistrar)
            section['1'] = {'ip': registrar['proxy_main']}
            proxy_backup = registrar.get('proxy_backup', None)
            if proxy_backup:
                section['2'] = {'ip': proxy_backup}

        if len(section) > 0:
            return {'sccp_call_managers': section}
