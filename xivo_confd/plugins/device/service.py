# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.helpers import errors

from xivo_confd.helpers.resource import CRUDService
from xivo_dao.helpers.db_manager import Session


class DeviceService(CRUDService):

    def __init__(self, dao, validator, notifier, search_engine, line_dao, line_device):
        super(DeviceService, self).__init__(dao, validator, notifier)
        self.search_engine = search_engine
        self.line_dao = line_dao
        self.line_device = line_device

    def create(self, resource, tenant_uuid=None):
        self.validator.validate_create(resource)
        created_resource = self.dao.create(resource, tenant_uuid=tenant_uuid)
        self.notifier.created(created_resource)
        return created_resource

    def edit(self, resource, updated_fields=None, tenant_uuid=None):
        with Session.no_autoflush:
            self.validator.validate_edit(resource)
        self.dao.edit(resource, tenant_uuid=tenant_uuid)
        self.notifier.edited(resource)

    def search(self, parameters, tenant_uuid=None):
        return self.search_engine.search(parameters, tenant_uuid=tenant_uuid)

    def synchronize(self, device, tenant_uuid=None):
        self.dao.synchronize(device, tenant_uuid=tenant_uuid)

    def reset_autoprov(self, device, tenant_uuid=None):
        for line in self.line_dao.find_all_by(device=device.id):
            self.line_device.dissociate(line, device)

    def assign_tenant(self, device, tenant_uuid=None):
        self.dao.edit(device, tenant_uuid=tenant_uuid)
        self.notifier.edited(device)

    def delete(self, resource, tenant_uuid=None):
        self.validator.validate_delete(resource)
        self.dao.delete(resource, tenant_uuid=tenant_uuid)
        self.notifier.deleted(resource)


class SearchEngine(object):

    PROVD_DEVICE_KEYS = [
        'id',
        'ip',
        'mac',
        'sn',
        'plugin',
        'vendor',
        'model',
        'version',
        'description',
    ]

    DIRECTION = ['asc',
                 'desc']

    DEFAULT_ORDER = 'ip'
    DEFAULT_DIRECTION = 'asc'

    def __init__(self, dao):
        self.dao = dao

    def search(self, parameters, tenant_uuid=None):
        self.validate_parameters(parameters)
        provd_devices = self.find_all_devices(parameters, tenant_uuid=tenant_uuid)
        provd_devices = self.filter_devices(provd_devices,
                                            parameters.get('search'))
        total = len(provd_devices)

        provd_devices = self.paginate_devices(provd_devices,
                                              parameters.get('offset', parameters.get('skip', 0)),
                                              parameters.get('limit'))

        items = [self.dao.build_device(provd_device)
                 for provd_device in provd_devices]

        return SearchResult(total=total, items=items)

    def validate_parameters(self, parameters):
        if 'direction' in parameters:
            if parameters['direction'] not in self.DIRECTION:
                raise errors.invalid_direction(parameters['direction'], self.DIRECTION)

        if 'order' in parameters:
            if parameters['order'] not in self.PROVD_DEVICE_KEYS:
                raise errors.invalid_ordering(parameters['order'], self.PROVD_DEVICE_KEYS)

    def find_all_devices(self, parameters, tenant_uuid=None):
        query = {key: value for key, value in parameters.iteritems()
                 if key in self.PROVD_DEVICE_KEYS}
        order = parameters.get('order', self.DEFAULT_ORDER)
        direction = parameters.get('direction', self.DEFAULT_DIRECTION)
        recurse = parameters.get('recurse', False)
        return self.dao.devices.list(search=query, order=order, direction=direction, tenant_uuid=tenant_uuid, recurse=recurse)['devices']

    def filter_devices(self, devices, search=None):
        if search is None:
            return devices

        search = search.lower()

        return [device for device in devices
                if self._matches_search(device, search)]

    def _matches_search(self, device, search_lowered):
        for key in self.PROVD_DEVICE_KEYS:
            if key in device and search_lowered in unicode(device[key]).lower():
                return True
        return False

    def paginate_devices(self, devices, offset=0, limit=None):
        if limit:
            return devices[offset:offset + limit]
        return devices[offset:]
