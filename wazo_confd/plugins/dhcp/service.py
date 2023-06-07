# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd._sysconfd import SysconfdPublisher
from wazo_confd.database import dhcp as dhcp_dao
from .notifier import DHCPNotifier
from .exceptions import InvalidInterfaces


class DHCPService:
    def __init__(self, notifier, sysconfd):
        self.notifier: DHCPNotifier = notifier
        self.sysconfd: SysconfdPublisher = sysconfd

    def get(self):
        return dhcp_dao.get()

    def edit(self, form: dict):
        if 'network_interfaces' in form and form['network_interfaces']:
            valid_interfaces = self.sysconfd.get_available_network_interfaces()
            valid_names = [interface['name'] for interface in valid_interfaces]
            proposed_interfaces = form['network_interfaces'].split(",")
            invalid_interfaces = [
                interface
                for interface in proposed_interfaces
                if interface not in valid_names
            ]
            if invalid_interfaces:
                raise InvalidInterfaces(invalid_interfaces)

        dhcp_dao.update(form)
        self.notifier.edited()
