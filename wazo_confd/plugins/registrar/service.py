# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.resource import CRUDService

from xivo_dao.helpers import errors
from xivo_dao.resources.utils.search import SearchResult


class RegistrarService(CRUDService):

    def __init__(self, dao, validator, notifier, search_engine, line_service, provd_client):
        super(RegistrarService, self).__init__(dao, validator, notifier)
        self.search_engine = search_engine
        self.line_service = line_service
        self.provd_client = provd_client

    def search(self, parameters):
        return self.search_engine.search(parameters)

    def create(self, resource):
        self.validator.validate_create(resource)
        created_resource = self.dao.create(resource)
        self.notifier.created(created_resource)
        return created_resource

    def edit(self, resource, updated_fields=None):
        super(RegistrarService, self).edit(resource, updated_fields=updated_fields)
        lines = self.line_service.find_all_by(registrar=resource.id)
        # Update all lines so they regenerate their configuration
        for line in lines:
            self.line_service.edit(line, [line.tenant_uuid])
        # Update autoprov config
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


class SearchEngine:

    REGISTRAR_KEYS = [
        'id',
        'displayname',
        'registrar_main',
        'registrar_main_port',
        'proxy_main',
        'proxy_main_port',
        'registrar_backup',
        'registrar_backup_port',
        'proxy_backup',
        'proxy_backup_port',
        'proxy_outbound',
        'proxy_outbound_port',
    ]

    DIRECTION = ['asc', 'desc']

    DEFAULT_ORDER = 'displayname'
    DEFAULT_DIRECTION = 'asc'

    def __init__(self, dao):
        self.dao = dao

    def search(self, parameters):
        self.validate_parameters(parameters)
        registrars = self.find_all_registrars(parameters)
        registrars = self.filter_registrars(registrars,
                                            parameters.get('search'))
        if registrars:
            total = len(registrars)
            registrars = self.paginate_registrars(
                registrars,
                parameters.get('offset', parameters.get('skip', 0)),
                parameters.get('limit')
            )
        else:
            registrars = []
            total = 0

        return SearchResult(total=total, items=registrars)

    def validate_parameters(self, parameters):
        if 'direction' in parameters:
            if parameters['direction'] not in self.DIRECTION:
                raise errors.invalid_direction(parameters['direction'], self.DIRECTION)

        if 'order' in parameters:
            if parameters['order'] not in self.REGISTRAR_KEYS:
                raise errors.invalid_ordering(parameters['order'], self.REGISTRAR_KEYS)

    def find_all_registrars(self, parameters):
        query = {key: value for key, value in parameters.items()
                 if key in self.REGISTRAR_KEYS}
        order = parameters.get('order', self.DEFAULT_ORDER)
        direction = parameters.get('direction', self.DEFAULT_DIRECTION)
        results = self.dao.find_all_by(search=query, order=order, direction=direction)
        return results

    def filter_registrars(self, registrars, search=None):
        if search is None:
            return registrars

        search = search.lower()

        return [registrar for registrar in registrars
                if self._matches_search(registrar, search)]

    def _matches_search(self, registrar, search_lowered):
        for key in self.REGISTRAR_KEYS:
            if hasattr(registrar, key) and search_lowered in str(getattr(registrar, key)).lower():
                return True
        return False

    def paginate_registrars(self, registrars, offset=0, limit=None):
        if limit:
            return registrars[offset:offset + limit]
        return registrars[offset:]
