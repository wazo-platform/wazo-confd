# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import requests

from xivo_confd.config import API_VERSION


# this function is not executed from the main thread
def self_check(config):
    if config['rest_api']['http']['enabled']:
        scheme = 'http'
        port = config['rest_api']['http']['port']
        verify = False
    elif config['rest_api']['https']['enabled']:
        scheme = 'https'
        port = config['rest_api']['https']['port']
        verify = config['rest_api']['https']['certificate']
    else:
        return False

    url = '{}://{}:{}/{}/infos'.format(scheme, 'localhost', port, API_VERSION)
    try:
        return requests.get(url, headers={'accept': 'application/json'}, verify=verify).status_code in (200, 401)
    except Exception:
        return False
