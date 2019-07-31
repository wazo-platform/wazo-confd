# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import string

from random import (
    choice,
    randrange,
)

from . import confd


def _random_ip(ips):
    ip = '.'.join(str(randrange(256)) for i in range(4))
    while ip in ips:
        ip = '.'.join(str(randrange(256)) for i in range(4))
    return ip


def generate_ip():
    response = confd.devices.get()
    ips = set(d['ip'] for d in response.items)
    return _random_ip(ips)


def generate_registrar(**params):
    name = "".join(choice(string.ascii_letters) for _ in range(20))
    ip = generate_ip()
    registrar = {
        'name': name,
        'id': name,
        'proxy_main_host': ip,
        'main_host': ip,
    }
    registrar.update(params)
    confd.registrars.post(registrar)
    return registrar


def delete_registrar(registrar_id, check=False):
    confd.registrars.delete(registrar_id)
