# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from .model import Registrar


class RegistrarDao:

    def __init__(self, client):
        self.client = client

    def create(self, registrar):
        result = self.client.configs.create(registrar.registrar)
        registrar = self.get(result['id'])
        return registrar

    def get(self, registrar_id):
        parameters = {
            'X_type': 'registrar',
            'id': registrar_id,
        }

        resources = self.client.configs.list(parameters)['configs']
        if len(resources) == 0:
            raise errors.not_found('Registrar', id=registrar_id)

        return Registrar(resources[0])

    def _find_registrars(self, **criteria):
        search = criteria.get('search', {})
        search['X_type'] = 'registrar'
        return self.client.configs.list(**criteria)['configs']

    def find_by(self, **criteria):
        registrars = self._find_registrars(**criteria)
        if registrars:
            return Registrar(registrars[0])

    def find_all_by(self, **criteria):
        registrars = self._find_registrars(**criteria)
        if registrars:
            return [Registrar(registrar) for registrar in registrars]
