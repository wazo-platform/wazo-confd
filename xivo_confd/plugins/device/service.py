# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.helpers import errors

from xivo_confd.helpers.resource import CRUDService


class DeviceService(CRUDService):

    def __init__(self, dao, validator, notifier, search_engine, line_dao):
        super(DeviceService, self).__init__(dao, validator, notifier)
        self.search_engine = search_engine
        self.line_dao = line_dao

    def search(self, parameters):
        return self.search_engine.search(parameters)

    def synchronize(self, device):
        self.dao.synchronize(device)

    def reset_autoprov(self, device):
        for line in self.line_dao.find_all_by(device=device.id):
            line.remove_device()
            self.line_dao.edit(line)
        self.dao.reset_autoprov(device)


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

    DIRECTION = {'asc': 1,
                 'desc': -1}

    DEFAULT_ORDER = 'ip'
    DEFAULT_DIRECTION = 'asc'

    def __init__(self, dao):
        self.dao = dao

    def search(self, parameters):
        self.validate_parameters(parameters)
        provd_devices = self.find_all_devices(parameters)
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

    def find_all_devices(self, parameters):
        query = {key: value for key, value in parameters.iteritems()
                 if key in self.PROVD_DEVICE_KEYS}
        order = parameters.get('order', self.DEFAULT_ORDER)
        direction = parameters.get('direction', self.DEFAULT_DIRECTION)
        sort_direction = self.DIRECTION[direction]
        return self.dao.devices.find(query, sort=(order, sort_direction))

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
