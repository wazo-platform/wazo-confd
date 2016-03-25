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

import string
import hashlib

from test_api import confd
from test_api import provd

from random import randrange, choice, randint, random


def generate_device(**params):
    mac, ip = generate_mac_and_ip()
    params.setdefault('mac', mac)
    params.setdefault('ip', ip)
    return add_device(**params)


def add_device(**params):
    response = confd.devices.post(params)
    return response.item


def delete_device(device_id, check=False):
    response = confd.devices(device_id).delete()
    if check:
        response.assert_ok()


def generate_mac_and_ip():
    return generate_mac(), generate_ip()


def generate_ip():
    response = confd.devices.get()
    ips = set(d['ip'] for d in response.items)
    return _random_ip(ips)


def generate_mac():
    response = confd.devices.get()
    macs = set(d['mac'] for d in response.items)
    return _random_mac(macs)


def generate_autoprov():
    mac, ip = generate_mac_and_ip()
    autoprov_id = 'autoprov{}'.format(randint(100000000, 9999999999))
    sip_username = "".join(choice(string.ascii_letters) for _ in range(20))
    random_id = hashlib.md5(str(random())).hexdigest()

    device = {'added': u'auto',
              'config': autoprov_id,
              'configured': True,
              'id': random_id,
              'ip': ip,
              'mac': mac,
              'model': u'6731i',
              'plugin': u'xivo-aastra-3.3.1-SP4',
              'remote_state_sip_username': sip_username,
              'vendor': u'Aastra',
              'version': u'3.3.1.4322'
              }

    config = {'id': autoprov_id,
              'transient': True,
              'parent_ids': ['autoprov'],
              'raw_config': {'sip_lines': {'1': {'username': sip_username}}}
              }

    provd.devices.add(device)
    provd.configs.add(config)

    return confd.devices(random_id).get().item


def _random_mac(macs):
    mac = ':'.join('{:02x}'.format(randrange(256)) for i in range(6))
    while mac in macs:
        mac = ':'.join('{:02x}'.format(randrange(256)) for i in range(6))
    return mac


def _random_ip(ips):
    ip = '.'.join(str(randrange(256)) for i in range(4))
    while ip in ips:
        ip = '.'.join(str(randrange(256)) for i in range(4))
    return ip


def generate_registrar(**params):
    name = "".join(choice(string.ascii_letters) for _ in range(20))
    ip = generate_ip()
    registrar = {'X_type': 'registrar',
                 'deletable': True,
                 'displayname': name,
                 'id': name,
                 'parent_ids': [],
                 'proxy_main': ip,
                 'proxy_backup': ip,
                 'registrar_main': ip,
                 'raw_config': {'X_key': 'xivo'},
                 'registrar_backup': ip}
    registrar.update(params)
    provd.configs.add(registrar)
    return registrar


def delete_registrar(registrar_id, check=False):
    provd.configs.remove(registrar_id)
