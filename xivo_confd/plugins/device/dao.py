# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_dao.helpers import errors

from wazo_provd_client.exceptions import ProvdError

from xivo_confd.plugins.device.model import Device

logger = logging.getLogger(__name__)


class DeviceDao(object):

    def __init__(self, client):
        self.client = client

    @property
    def devices(self):
        return self.client.devices

    @property
    def configs(self):
        return self.client.configs

    def get(self, id):
        try:
            provd_device = self.devices.get(id)
        except ProvdError:
            raise errors.not_found('Device', id=id)
        return self.build_device(provd_device)

    def build_device(self, provd_device):
        try:
            provd_config = self.configs.get(provd_device['config'])
        except (KeyError, ProvdError):
            provd_config = None
        return Device(provd_device, provd_config)

    def find_by(self, **criteria):
        provd_devices = self.devices.list(criteria)['devices']
        if provd_devices:
            return self.build_device(provd_devices[0])

    def create(self, device):
        new_device = self.new_device()
        new_device.merge(device)
        self.edit(new_device)
        return new_device

    def new_device(self):
        config_id = self.configs.autocreate()['id']
        device_id = self.devices.create({'config': config_id})['id']
        return self.get(device_id)

    def create_or_update(self, device):
        try:
            self.devices.update(device.device)
        except ProvdError:
            self.devices.create(device.device)

        try:
            self.configs.update(device.config)
        except ProvdError:
            self.configs.create(device.config)

    def edit(self, device):
        self.devices.update(device.device)
        self.configs.update(device.config)

    def delete(self, device):
        self.devices.delete(device.id)
        self._remove_config(device._config)

    def reset_autoprov(self, device):
        old_config = device._config
        autoprov_id = self.configs.autocreate()['id']
        autoprov_config = self.configs.get(autoprov_id)
        device.reset_autoprov(autoprov_config)
        self.edit(device)
        self._remove_config(old_config)

    def _remove_config(self, config):
        try:
            if config is not None:
                self.configs.delete(config['id'])
        except ProvdError:
            pass
        logger.debug("removed config %s", config['id'])

    def synchronize(self, device):
        self.devices.synchronize(device.id)

    def plugins(self):
        return self.client.plugins.list()['plugins']

    def device_templates(self):
        templates = self.configs.list({'X_type': 'device'})['configs']
        return [t['id'] for t in templates]

    def get_registrar(self, registrar_id):
        registrars = self.configs.list({'X_type': 'registrar',
                                        'id': registrar_id})['configs']
        if not registrars:
            raise errors.not_found('Registrar', id=registrar_id)
        return registrars[0]

    def registrars(self):
        registrars = self.configs.list({'X_type': 'registrar'})['configs']
        return [r['id'] for r in registrars]
