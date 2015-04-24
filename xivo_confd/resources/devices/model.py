# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

import abc

from xivo_dao.data_handler.device.model import Device


class ProvdDevice(object):

    def __init__(self, device_converter, config_converter):
        self.device_converter = device_converter
        self.config_converter = config_converter

    @property
    def device_id(self):
        return self.device_converter.device_id

    @property
    def config_id(self):
        return self.config_converter.config_id

    def extract_model(self):
        fields = self.device_converter.extract_model()
        fields.update(self.config_converter.extract_model())
        return Device(**fields)

    def extract_device(self):
        return self.device_converter.extract_provd()

    def extract_config(self):
        return self.config_converter.extract_provd()

    def update(self, model):
        self.device_converter.update(model)
        self.config_converter.update(model)

    def reset_autoprov(self, config):
        self.device_converter.reset_autoprov(config['id'])
        self.config_converter = ConfigConverter(config)

    def update_lines(self, lines):
        self.device_converter.update_config_id(self.device_id)
        self.config_converter.update_lines(lines)


class DeviceConverter(object):

    DEVICE_FIELDS = [
        'id',
        'ip',
        'mac',
        'sn',
        'plugin',
        'vendor',
        'model',
        'version',
        'description',
        'options',
    ]

    def __init__(self, device):
        self.device = device

    @property
    def device_id(self):
        return self.device['id']

    def extract_model(self):
        fields = {name: self.device[name]
                  for name in self.DEVICE_FIELDS
                  if name in self.device}
        fields['status'] = self.determine_status()
        return fields

    def determine_status(self):
        if self.device.get('configured', False):
            if self.device.get('config', '').startswith('autoprov'):
                return 'autoprov'
            return 'configured'
        return 'not_configured'

    def extract_provd(self):
        return self.device

    def update(self, model):
        device = {name: getattr(model, name)
                  for name in self.DEVICE_FIELDS
                  if getattr(model, name) is not None}

        if 'mac' in device:
            device['mac'] = device['mac'].lower()

        self.device.update(device)

    def reset_autoprov(self, config_id):
        self.device.pop('options', None)
        self.device['config'] = config_id

    def update_config_id(self, config_id):
        self.device['config'] = config_id


class ConfigConverter(object):

    def __init__(self, config):
        self.config = config

    @property
    def config_id(self):
        return self.config['id']

    def extract_model(self):
        return {'template_id': self.config.get('configdevice')}

    def extract_provd(self):
        return self.config

    def update(self, model):
        self.remove_device_template()
        if model.template_id:
            self.add_device_template(model.template_id)

    def remove_device_template(self):
        configdevice = self.config.pop('configdevice', None)
        if configdevice and configdevice in self.config['parent_ids']:
            self.config['parent_ids'].remove(configdevice)

    def add_device_template(self, configdevice):
        self.config['configdevice'] = configdevice
        self.config['parent_ids'].append(configdevice)

    def update_lines(self, lines):
        self.empty_lines(lines)
        self.fill_lines(lines)

    def empty_lines(self, lines):
        sections = set(line.section for line in lines)
        for section in sections:
            self.config['raw_config'][section] = {}

    def fill_lines(self, lines):
        for line in lines:
            config = line.build()
            self.config['raw_config'][line.section].update(config)


class EmptyConfigConverter(object):

    def extract_model(self):
        return {'status': 'not_configured'}

    def extract_provd(self):
        raise Exception("provd config does not exist")

    def update(self, model):
        raise Exception("provd config does not exist")

    def update_lines(self, lines):
        raise Exception("provd config does not exist")

    @property
    def config_id(self):
        raise Exception("provd config does not exist")


class LineConverter(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def section(self):
        return

    @abc.abstractmethod
    def build(self):
        return


class LineSIPConverter(LineConverter):

    section = 'sip_lines'

    def __init__(self, registrar, line, extension):
        self.registrar = registrar
        self.line = line
        self.extension = extension

    def build(self):
        slot = {'auth_username': self.line.name,
                'username': self.line.name,
                'password': self.line.secret,
                'display_name': self.line.extract_displayname(),
                'number': self.extension.exten,
                'registrar_ip': self.registrar['registrar_main'],
                'proxy_ip': self.registrar['proxy_main']}

        proxy_backup = self.registrar.get('proxy_backup', '')
        if proxy_backup:
            slot['backup_proxy_ip'] = proxy_backup
            slot['backup_registrar_ip'] = self.registrar['registrar_backup']

        return {self.line.device_slot: slot}

    def __eq__(self, other):
        return all([self.registrar == other.registrar,
                    self.line == other.line,
                    self.extension == other.extension])

    def __repr__(self):
        tpl = "<LineSIPConverter line_id:{} extension_id:{} registrar_id:{}>"
        return tpl.format(self.line.id, self.extension.id, self.registrar['id'])


class LineSCCPConverter(LineConverter):

    section = 'sccp_call_managers'

    def __init__(self, registrar):
        self.registrar = registrar

    def build(self):
        slot = {1: {'ip': self.registar['proxy_main']}}

        proxy_backup = self.registrar.get('proxy_backup', '')
        if proxy_backup:
            slot[2] = {'ip': proxy_backup}

        return slot

    def __eq__(self, other):
        return self.registrar == other.registrar

    def __repr__(self):
        return "<LineSCCPConverter {}>".format(self.registrar)
