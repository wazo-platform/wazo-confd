# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult

from .model import Registrar


class RegistrarDao:

    REGISTRAR_KEYS = {
        'id': 'id',
        'name': 'displayname',
        'main_host': 'registrar_main',
        'main_port': 'registrar_main_port',
        'backup_host': 'registrar_backup',
        'backup_port': 'registrar_backup_port',
        'proxy_main_host': 'proxy_main',
        'proxy_main_port': 'proxy_main_port',
        'proxy_backup_host': 'proxy_backup',
        'proxy_backup_port': 'proxy_backup_port',
        'outbound_proxy_host': 'proxy_outbound',
        'outbound_proxy_port': 'proxy_outbound_port',
    }

    DIRECTION = set(('asc', 'desc'))

    DEFAULT_ORDER = 'name'
    DEFAULT_DIRECTION = 'asc'

    def __init__(self, client):
        self.client = client

    def create(self, registrar):
        result = self.client.configs.create(registrar.as_dict())
        registrar = self.get(result['id'])
        return registrar

    def get(self, registrar_id):
        parameters = {
            'X_type': 'registrar',
            'id': registrar_id,
        }

        resources = self.client.configs.list(parameters)['configs']
        if not resources:
            raise errors.not_found('Registrar', id=registrar_id)

        return Registrar(resources[0])

    def _validate_parameters(self, parameters):
        if 'direction' in parameters:
            if parameters['direction'] not in self.DIRECTION:
                raise errors.invalid_direction(parameters['direction'], self.DIRECTION)

        if 'order' in parameters:
            if parameters['order'] not in self.REGISTRAR_KEYS:
                raise errors.invalid_ordering(parameters['order'], self.REGISTRAR_KEYS)

    def _find_all_registrars(self, parameters):
        query = {'X_type': 'registrar'}
        order = self.REGISTRAR_KEYS.get(parameters.pop('order', self.DEFAULT_ORDER))
        direction = parameters.pop('direction', self.DEFAULT_DIRECTION)
        results = self.client.configs.list(search=query, order=order, direction=direction)['configs']
        return results

    def _filter_registrars(self, registrars, search=None):
        if search is None:
            return registrars

        if search.get('search'):
            search_text = search.pop('search')
            registrars = [registrar for registrar in registrars
                          if self._matches_text_search(registrar, search_text)]
        if search:
            registrars = [registrar for registrar in registrars
                          if self._matches_search(registrar, search)]
        return registrars

    def _matches_search(self, registrar, search):
        for key, value in search.items():
            if key in self.REGISTRAR_KEYS:
                real_key = self.REGISTRAR_KEYS[key]
                if real_key in registrar and str(value).lower() in str(registrar[real_key]).lower():
                    return True
        return False

    def _matches_text_search(self, registrar, search):
        for key in self.REGISTRAR_KEYS.values():
            if key in registrar and str(search).lower() in str(registrar[key]).lower():
                return True
        return False

    def _find_registrars(self, criteria):
        self._validate_parameters(criteria)
        registrars = self._find_all_registrars(criteria)
        registrars = self._filter_registrars(registrars, search=criteria)
        return registrars

    def _paginate_registrars(self, registrars, offset=0, limit=None):
        if limit:
            return registrars[offset:offset + limit]
        return registrars[offset:]

    def find_by(self, **criteria):
        registrars = self._find_registrars(criteria)
        if registrars:
            return Registrar(registrars[0])

    def get_by(self, **criteria):
        registrar = self.find_by(**criteria)
        if not registrar:
            raise errors.not_found('Registrar', criteria)
        return registrar

    def search(self, **criteria):
        registrars = self._find_registrars(criteria)
        if registrars:
            total = len(registrars)
            registrars = self._paginate_registrars(
                registrars,
                criteria.get('offset', criteria.get('skip', 0)),
                criteria.get('limit')
            )
        else:
            registrars = []
            total = 0
        registrars = [Registrar(result) for result in registrars]
        return SearchResult(total=total, items=registrars)

    def edit(self, new_registrar):
        self.client.configs.update(new_registrar.as_dict())

    def delete(self, registrar):
        self.client.configs.delete(registrar.id)
