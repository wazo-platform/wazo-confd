# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class Device:
    @classmethod
    def from_args(cls, **kwargs):
        device = cls({}, {'parent_ids': []})
        for key, value in kwargs.items():
            setattr(device, key, value)
        return device

    def __init__(self, device, config=None):
        self.device = device
        self._config = config

    def set_value(self, name, value):
        if value is None:
            if name in self.device:
                del self.device[name]
        else:
            self.device[name] = value

    @property
    def config(self):
        if self._config is None:
            raise Exception(
                "Provd Device has no config associated. The device may be corrupt"
            )
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def id(self):
        return self.device['id']

    @id.setter
    def id(self, value):
        self.device['id'] = value

    @property
    def ip(self):
        return self.device.get('ip')

    @ip.setter
    def ip(self, value):
        self.set_value('ip', value)

    @property
    def mac(self):
        return self.device.get('mac')

    @mac.setter
    def mac(self, value):
        value = value.lower() if value else None
        self.set_value('mac', value)

    @property
    def sn(self):
        return self.device.get('sn')

    @sn.setter
    def sn(self, value):
        self.set_value('sn', value)

    @property
    def plugin(self):
        return self.device.get('plugin')

    @plugin.setter
    def plugin(self, value):
        self.set_value('plugin', value)

    @property
    def vendor(self):
        return self.device.get('vendor')

    @vendor.setter
    def vendor(self, value):
        self.set_value('vendor', value)

    @property
    def model(self):
        return self.device.get('model')

    @model.setter
    def model(self, value):
        self.set_value('model', value)

    @property
    def version(self):
        return self.device.get('version')

    @version.setter
    def version(self, value):
        self.set_value('version', value)

    @property
    def description(self):
        return self.device.get('description')

    @description.setter
    def description(self, value):
        self.set_value('description', value)

    @property
    def options(self):
        return self.device.get('options')

    @options.setter
    def options(self, value):
        self.set_value('options', value)

    @property
    def status(self):
        if self.device.get('configured', False):
            if self.device.get('config', '').startswith('autoprov'):
                return 'autoprov'
            return 'configured'
        return 'not_configured'

    @property
    def template_id(self):
        return self.config.get('configdevice')

    @template_id.setter
    def template_id(self, value):
        configdevice = self.config.pop('configdevice', None)
        if configdevice and configdevice in self.config['parent_ids']:
            self.config['parent_ids'].remove(configdevice)

        if value:
            self.config['configdevice'] = value
            self.config['parent_ids'].append(value)

    @property
    def tenant_uuid(self):
        return self.device.get('tenant_uuid')

    @tenant_uuid.setter
    def tenant_uuid(self, value):
        self.set_value('tenant_uuid', value)

    @property
    def is_new(self):
        return self.device.get('is_new')

    def is_autoprov(self):
        return 'autoprov' in self.config['parent_ids']

    def update_config(self, config):
        self.device['config'] = config['id']
        self.config = config

    def reset_autoprov(self, config):
        if 'options' in self.device:
            del self.device['options']
        self.update_config(config)

    def merge(self, other):
        self.device.update(other.device)
        if other.template_id is not None:
            self.template_id = other.template_id
