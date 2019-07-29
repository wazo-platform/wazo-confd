# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.resource import CRUDService


class RegistrarService(CRUDService):

    def __init__(self, dao, validator, notifier, line_service, device_updater, provd_client):
        super(RegistrarService, self).__init__(dao, validator, notifier)
        self.line_service = line_service
        self.device_updater = device_updater
        self.provd_client = provd_client

    def search(self, parameters):
        return self.dao.search(**parameters)

    def create(self, resource):
        self.validator.validate_create(resource)
        created_resource = self.dao.create(resource)
        self.notifier.created(created_resource)
        return created_resource

    def edit(self, resource, updated_fields=None):
        super(RegistrarService, self).edit(resource, updated_fields=updated_fields)
        lines = self.line_service.find_all_by(registrar=resource.id)
        devices_updated = set()
        # Update all affected devices
        for line in lines:
            if line.device_id not in devices_updated:
                self.device_updater.update_for_line(line)
                devices_updated.add(line.device_id)

        # Update default autoprov config
        autoprov_config = self.provd_client.configs.get('autoprov')
        autoprov_sip_line = autoprov_config['raw_config']['sip_lines']['1']
        self._update_sip(resource.registrar, autoprov_sip_line)
        autoprov_sccp_lines = autoprov_config['raw_config']['sccp_call_managers']
        self._update_sccp(resource.registrar, autoprov_sccp_lines)
        self.provd_client.configs.update(autoprov_config)

    def _update_sip(self, registrar, config):
        config['registrar_ip'] = registrar['registrar_main']
        config['proxy_ip'] = registrar['proxy_main']
        optional_keys = {
            'registrar_port': 'registrar_main_port',
            'proxy_port': 'proxy_main_port',
            'backup_proxy_ip': 'proxy_backup',
            'backup_proxy_port': 'proxy_backup_port',
            'backup_registrar_ip': 'registrar_backup',
            'backup_registrar_port': 'registrar_backup_port',
            'outbound_proxy_ip': 'proxy_outbound',
            'outbound_proxy_port': 'proxy_outbound_port',
        }

        for real_key, registrar_key in optional_keys.items():
            value = registrar.get(registrar_key)
            if value:
                config[real_key] = value

    def _update_sccp(self, registrar, config):
        main = config.get('1')
        backup = config.get('2')
        if main:
            main['ip'] = registrar['proxy_main']
        if backup:
            backup['ip'] = registrar['proxy_backup']
