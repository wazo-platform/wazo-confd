# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_dao.helpers import errors

from xivo_provd_client.error import NotFoundError

from xivo_confd.plugins.device.model import Device

logger = logging.getLogger(__name__)


class DeviceDao(object):

    def __init__(self, client):
        self.client = client

    @property
    def devices(self):
        return self.client.device_manager()

    @property
    def configs(self):
        return self.client.config_manager()

    def get(self, id):
        try:
            provd_device = self.devices.get(id)
        except NotFoundError:
            raise errors.not_found('Device', id=id)
        return self.build_device(provd_device)

    def build_device(self, provd_device):
        try:
            provd_config = self.configs.get(provd_device['config'])
        except (KeyError, NotFoundError):
            provd_config = None
        return Device(provd_device, provd_config)

    def find_by(self, **criteria):
        provd_devices = self.devices.find(criteria)
        if provd_devices:
            return self.build_device(provd_devices[0])

    def create(self, device):
        new_device = self.new_device()
        new_device.merge(device)
        self.edit(new_device)
        return new_device

    def new_device(self):
        config_id = self.configs.autocreate()
        device_id = self.devices.add({'config': config_id})
        return self.get(device_id)

    def create_or_update(self, device):
        try:
            self.devices.update(device.device)
        except NotFoundError:
            self.devices.add(device.device)

        try:
            self.configs.update(device.config)
        except NotFoundError:
            self.configs.add(device.config)

    def edit(self, device):
        self.devices.update(device.device)
        self.configs.update(device.config)

    def delete(self, device):
        self.devices.remove(device.id)
        self._remove_config(device._config)

    def reset_autoprov(self, device):
        old_config = device._config
        autoprov_id = self.configs.autocreate()
        autoprov_config = self.configs.get(autoprov_id)
        device.reset_autoprov(autoprov_config)
        self.edit(device)
        self._remove_config(old_config)

    def _remove_config(self, config):
        try:
            if config is not None:
                self.configs.remove(config['id'])
        except NotFoundError:
            pass
        logger.debug("removed config %s", config['id'])

    def synchronize(self, device):
        self.devices.synchronize(device.id)

    def plugins(self):
        return self.client.plugin_manager().plugins()

    def device_templates(self):
        templates = self.configs.find({'X_type': 'device'})
        return [t['id'] for t in templates]

    def get_registrar(self, registrar_id):
        registrars = self.configs.find({'X_type': 'registrar',
                                        'id': registrar_id})
        if not registrars:
            raise errors.not_found('Registrar', id=registrar_id)
        return registrars[0]

    def registrars(self):
        registrars = self.configs.find({'X_type': 'registrar'})
        return [r['id'] for r in registrars]
