# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class Registrar:

    @classmethod
    def from_args(cls, **kwargs):
        baseregistrar = {
            'X_type': 'registrar',
            'parent_ids': [],
            'raw_config': {'X_key': 'wazo'},
        }
        registrar = cls(baseregistrar)
        for key, value in kwargs.items():
            setattr(registrar, key, value)
        return registrar

    def __init__(self, registrar):
        self._registrar = registrar

    @property
    def id(self):
        return self._registrar.get('id')

    @id.setter
    def id(self, value):
        self._registrar['id'] = value

    @property
    def deletable(self):
        return self._registrar.get('deletable')

    @deletable.setter
    def deletable(self, value):
        self._registrar['deletable'] = value

    @property
    def name(self):
        return self._registrar.get('displayname')

    @name.setter
    def name(self, value):
        self._registrar['displayname'] = value

    @property
    def main_host(self):
        return self._registrar.get('registrar_main')

    @main_host.setter
    def main_host(self, value):
        self._registrar['registrar_main'] = value

    @property
    def main_port(self):
        return self._registrar.get('registrar_main_port')

    @main_port.setter
    def main_port(self, value):
        self._registrar['registrar_main_port'] = value

    @property
    def backup_host(self):
        return self._registrar.get('registrar_backup')

    @backup_host.setter
    def backup_host(self, value):
        self._registrar['registrar_backup'] = value

    @property
    def backup_port(self):
        return self._registrar.get('registrar_backup_port')

    @backup_port.setter
    def backup_port(self, value):
        self._registrar['registrar_backup_port'] = value

    @property
    def proxy_main_host(self):
        return self._registrar.get('proxy_main')

    @proxy_main_host.setter
    def proxy_main_host(self, value):
        self._registrar['proxy_main'] = value

    @property
    def proxy_main_port(self):
        return self._registrar.get('proxy_main_port')

    @proxy_main_port.setter
    def proxy_main_port(self, value):
        self._registrar['proxy_main_port'] = value

    @property
    def proxy_backup_host(self):
        return self._registrar.get('proxy_backup')

    @proxy_backup_host.setter
    def proxy_backup_host(self, value):
        self._registrar['proxy_backup'] = value

    @property
    def proxy_backup_port(self):
        return self._registrar.get('proxy_backup_port')

    @proxy_backup_port.setter
    def proxy_backup_port(self, value):
        self._registrar['proxy_backup_port'] = value

    @property
    def outbound_proxy_host(self):
        return self._registrar.get('proxy_outbound')

    @outbound_proxy_host.setter
    def outbound_proxy_host(self, value):
        self._registrar['proxy_outbound'] = value

    @property
    def outbound_proxy_port(self):
        return self._registrar.get('proxy_outbound_port')

    @outbound_proxy_port.setter
    def outbound_proxy_port(self, value):
        self._registrar['proxy_outbound_port'] = value

    def as_dict(self):
        return self._registrar.copy()
