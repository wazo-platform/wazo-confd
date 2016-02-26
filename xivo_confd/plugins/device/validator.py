# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import (Validator,
                                          ValidationGroup,
                                          Optional,
                                          UniqueField,
                                          RegexField,
                                          MemberOfSequence)


IP_REGEX = r'(1?\d{1,2}|2([0-4][0-9]|5[0-5]))(\.(1?\d{1,2}|2([0-4][0-9]|5[0-5]))){3}$'
MAC_REGEX = r'^([0-9A-Fa-f]{2})(:[0-9A-Fa-f]{2}){5}$'


class OptionsValidator(Validator):

    def validate(self, device):
        options = device.options or {}
        if not isinstance(options, dict):
            raise errors.wrong_type('options', 'dict-like structure',
                                    options=options)
        if 'switchboard' in options and not isinstance(options['switchboard'], bool):
            raise errors.wrong_type('options.switchboard', 'boolean',
                                    options=options)


class MacChanged(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, device):
        mac = device.mac
        if mac is not None:
            found = self.dao.find_by(mac=mac)
            if found is not None and found.id != device.id:
                raise errors.resource_exists('Device', mac=mac)


class DeviceNotAssociated(Validator):

    def __init__(self, line_dao):
        self.line_dao = line_dao

    def validate(self, device):
        lines = self.line_dao.find_all_by(device=device.id)
        if lines:
            ids = tuple(l.id for l in lines)
            raise errors.resource_associated('Device', 'Line',
                                             device_id=device.id, line_ids=ids)


def build_validator(device_dao, line_dao):
    return ValidationGroup(
        common=[
            Optional('ip',
                     RegexField.compile('ip', IP_REGEX, "wrong type: IP Address")
                     ),
            Optional('mac',
                     RegexField.compile('mac', MAC_REGEX, "wrong type: MAC Address")
                     ),
            Optional('plugin',
                     MemberOfSequence('plugin', device_dao.plugins, 'Plugin')
                     ),
            Optional('template_id',
                     MemberOfSequence('template_id', device_dao.device_templates, 'DeviceTemplate')
                     ),
            OptionsValidator(),
        ],
        create=[
            Optional('mac',
                     UniqueField('mac',
                                 lambda mac: device_dao.find_by(mac=mac),
                                 'Device')
                     ),
        ],
        edit=[
            MacChanged(device_dao)
        ],
        delete=[
            DeviceNotAssociated(line_dao)
        ],
    )
