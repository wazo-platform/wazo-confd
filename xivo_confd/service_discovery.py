# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import requests

from xivo_confd.config import API_VERSION


# this function is not executed from the main thread
def self_check(config):
    if config['rest_api']['http']['enabled']:
        scheme = 'http'
        port = config['rest_api']['http']['port']
    elif config['rest_api']['https']['enabled']:
        scheme = 'https'
        port = config['rest_api']['https']['port']
    else:
        return False

    url = '{}://{}:{}/{}/infos'.format(scheme, 'localhost', port, API_VERSION)
    try:
        return requests.get(url, headers={'accept': 'application/json'}, verify=False).status_code in (200, 401)
    except Exception:
        return False
