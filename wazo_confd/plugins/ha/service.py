# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm.session import make_transient


class HAService:
    def __init__(self, sip_general_service, registrar_service, notifier, sysconfd):
        self.notifier = notifier
        self.registrar_service = registrar_service
        self.sip_general_service = sip_general_service
        self.sysconfd = sysconfd

    def get(self):
        return self.sysconfd.get_ha_config()

    def edit(self, form):
        if form['node_type'] == 'disabled':
            current_node_type = self.sysconfd.get_ha_config()['node_type']
            self._update_sip_general_options(
                {'minexpiry': '60', 'maxexpiry': '3600', 'defaultexpiry': '120'}
            )
            if current_node_type != 'slave':
                self._update_provisioning_options(remote_address=None)
        elif form['node_type'] == 'master':
            self._update_sip_general_options(
                {'minexpiry': '180', 'maxexpiry': '300', 'defaultexpiry': '240'}
            )
            self._update_provisioning_options(form['remote_address'])
        self.notifier.edited(form)

    def _update_sip_general_options(self, update_options):
        sip_general_options = self.sip_general_service.list()
        for option in sip_general_options:
            make_transient(option)
            if option.var_name in update_options:
                option.var_val = update_options[option.var_name]
        self.sip_general_service.edit(sip_general_options)

    def _update_provisioning_options(self, remote_address):
        registrars = self.registrar_service.search(parameters={})
        for registrar in registrars.items:
            registrar.backup_host = remote_address
            registrar.proxy_backup_host = remote_address
            self.registrar_service.edit(registrar)
