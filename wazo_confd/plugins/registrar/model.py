# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
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
        self.registrar = registrar

    @property
    def id(self):
        return self.registrar.get('id')

    @id.setter
    def id(self, value):
        self.registrar['id'] = value

    @property
    def displayname(self):
        return self.registrar.get('displayname')

    @displayname.setter
    def displayname(self, value):
        self.registrar['displayname'] = value

    @property
    def registrar_main(self):
        return self.registrar.get('registrar_main')

    @registrar_main.setter
    def registrar_main(self, value):
        self.registrar['registrar_main'] = value

    @property
    def registrar_main_port(self):
        return self.registrar.get('registrar_main_port')

    @registrar_main_port.setter
    def registrar_main_port(self, value):
        self.registrar['registrar_main_port'] = value

    @property
    def registrar_backup(self):
        return self.registrar.get('registrar_backup')

    @registrar_backup.setter
    def registrar_backup(self, value):
        self.registrar['registrar_backup'] = value

    @property
    def registrar_backup_port(self):
        return self.registrar.get('registrar_backup_port')

    @registrar_backup_port.setter
    def registrar_backup_port(self, value):
        self.registrar['registrar_backup_port'] = value

    @property
    def proxy_main(self):
        return self.registrar.get('proxy_main')

    @proxy_main.setter
    def proxy_main(self, value):
        self.registrar['proxy_main'] = value

    @property
    def proxy_main_port(self):
        return self.registrar.get('proxy_main_port')

    @proxy_main_port.setter
    def proxy_main_port(self, value):
        self.registrar['proxy_main_port'] = value

    @property
    def proxy_backup(self):
        return self.registrar.get('proxy_backup')

    @proxy_backup.setter
    def proxy_backup(self, value):
        self.registrar['proxy_backup'] = value

    @property
    def proxy_backup_port(self):
        return self.registrar.get('proxy_backup_port')

    @proxy_backup_port.setter
    def proxy_backup_port(self, value):
        self.registrar['proxy_backup_port'] = value

    @property
    def proxy_outbound(self):
        return self.registrar.get('proxy_outbound')

    @proxy_outbound.setter
    def proxy_outbound(self, value):
        self.registrar['proxy_outbound'] = value

    @property
    def proxy_outbound_port(self):
        return self.registrar.get('proxy_outbound_port')

    @proxy_outbound_port.setter
    def proxy_outbound_port(self, value):
        self.registrar['proxy_outbound_port'] = value
