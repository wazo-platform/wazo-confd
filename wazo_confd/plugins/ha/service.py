# Copyright 2019-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class HAService:
    def __init__(self, registrar_service, notifier, sysconfd):
        self.notifier = notifier
        self.registrar_service = registrar_service
        self.sysconfd = sysconfd

    def get(self):
        return self.sysconfd.get_ha_config()

    def edit(self, form):
        if form['node_type'] == 'disabled':
            current_node_type = self.sysconfd.get_ha_config()['node_type']
            if current_node_type != 'slave':
                self._update_provisioning_options(remote_address=None)
        elif form['node_type'] == 'master':
            self._update_provisioning_options(form['remote_address'])
        self.notifier.edited(form)

    def _update_provisioning_options(self, remote_address):
        registrars = self.registrar_service.search(parameters={})
        for registrar in registrars.items:
            registrar.backup_host = remote_address
            registrar.proxy_backup_host = remote_address
            self.registrar_service.edit(registrar)
