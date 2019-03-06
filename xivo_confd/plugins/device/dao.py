# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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

    def get(self, id, tenant_uuid=None):
        try:
            provd_device = self.devices.get(id, tenant_uuid=tenant_uuid)
        except ProvdError as e:
            if e.status_code == 404:
                raise errors.not_found('Device', id=id)
            raise
        return self.build_device(provd_device)

    def build_device(self, provd_device):
        try:
            provd_config = self.configs.get(provd_device['config'])
        except (KeyError, ProvdError):
            provd_config = None
        return Device(provd_device, provd_config)

    def find_by(self, tenant_uuid=None, **criteria):
        kwargs = {}
        if tenant_uuid is None:
            kwargs['recurse'] = True
        else:
            kwargs['tenant_uuid'] = tenant_uuid

        provd_devices = self.devices.list(criteria, **kwargs)['devices']
        if provd_devices:
            return self.build_device(provd_devices[0])

    def create(self, device, tenant_uuid=None):
        new_device = self.new_device(tenant_uuid=tenant_uuid)
        new_device.merge(device)
        self.edit(new_device, tenant_uuid=tenant_uuid)
        return new_device

    def new_device(self, tenant_uuid=None):
        config_id = self.configs.autocreate()['id']
        device_id = self.devices.create({'config': config_id}, tenant_uuid=tenant_uuid)['id']
        return self.get(device_id, tenant_uuid=tenant_uuid)

    def create_or_update(self, device, tenant_uuid=None):
        try:
            self.devices.update(device.device, tenant_uuid=tenant_uuid)
        except ProvdError as e:
            if e.status_code != 404:
                raise
            self.devices.create(device.device, tenant_uuid=tenant_uuid)

        try:
            self.configs.update(device.config)
        except ProvdError as e:
            if e.status_code != 404:
                raise
            self.configs.create(device.config)

    def edit(self, device, tenant_uuid=None):
        self.devices.update(device.device, tenant_uuid=tenant_uuid)
        self.configs.update(device.config)

    def delete(self, device, tenant_uuid=None):
        try:
            self.devices.delete(device.id, tenant_uuid=tenant_uuid)
        except ProvdError as e:
            if e.status_code != 404:
                raise
        self._remove_config(device._config)

    def reset_autoprov(self, device, tenant_uuid=None):
        old_config = device._config
        autoprov_id = self.configs.autocreate()['id']
        autoprov_config = self.configs.get(autoprov_id)
        device.reset_autoprov(autoprov_config)
        self.edit(device, tenant_uuid=device.tenant_uuid)
        self._remove_config(old_config)

    def _remove_config(self, config):
        if config is None:
            return
        try:
            self.configs.delete(config['id'])
        except ProvdError as e:
            if e.status_code != 404:
                raise
        logger.debug("removed config %s", config['id'])

    def synchronize(self, device, tenant_uuid=None):
        self.devices.synchronize(device.id, tenant_uuid=tenant_uuid)

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
