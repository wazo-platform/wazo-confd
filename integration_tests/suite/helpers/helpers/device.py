# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

import string
import hashlib

from random import (
    choice,
    randint,
    random,
    randrange,
)

from . import confd, provd


def generate_device(**params):
    mac, ip = generate_mac_and_ip()
    params.setdefault('mac', mac)
    params.setdefault('ip', ip)
    return add_device(**params)


def add_device(wazo_tenant=None, **params):
    response = confd.devices.post(params, wazo_tenant=wazo_tenant)
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

    device = {
        'added': 'auto',
        'config': autoprov_id,
        'configured': True,
        'id': random_id,
        'ip': ip,
        'mac': mac,
        'model': '6731i',
        'plugin': 'xivo-aastra-3.3.1-SP4',
        'remote_state_sip_username': sip_username,
        'vendor': 'Aastra',
        'version': '3.3.1.4322'
    }

    config = {
        'id': autoprov_id,
        'transient': True,
        'parent_ids': ['autoprov'],
        'raw_config': {'sip_lines': {'1': {'username': sip_username}}}
    }

    provd.devices.create(device)
    provd.configs.create(config)

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
    registrar = {
        'X_type': 'registrar',
        'deletable': True,
        'displayname': name,
        'id': name,
        'parent_ids': [],
        'proxy_main': ip,
        'proxy_backup': ip,
        'registrar_main': ip,
        'raw_config': {'X_key': 'xivo'},
        'registrar_backup': ip,
    }
    registrar.update(params)
    provd.configs.create(registrar)
    return registrar


def delete_registrar(registrar_id, check=False):
    provd.configs.delete(registrar_id)
