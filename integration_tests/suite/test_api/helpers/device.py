from test_api import confd
from random import randrange


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
    response = confd.devices.get()
    macs = set(d['mac'] for d in response.items)
    ips = set(d['ip'] for d in response.items)

    return _random_mac(macs), _random_ip(ips)


def _random_mac(macs):
    mac = ':'.join('{:02X}'.format(randrange(256)) for i in range(6))
    while mac in macs:
        mac = ':'.join('{:02X}'.format(randrange(256)) for i in range(6))
    return mac


def _random_ip(ips):
    ip = '.'.join(str(randrange(256)) for i in range(4))
    while ip in ips:
        ip = '.'.join(str(randrange(256)) for i in range(4))
    return ip
