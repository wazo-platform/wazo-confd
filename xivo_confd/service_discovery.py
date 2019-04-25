# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests

from xivo_confd.config import API_VERSION


# this function is not executed from the main thread
def self_check(config):
    port = config['rest_api']['port']

    url = '{}://{}:{}/{}/infos'.format('https', 'localhost', port, API_VERSION)
    try:
        return requests.get(url, headers={'accept': 'application/json'}, verify=False).status_code in (200, 401)
    except Exception:
        return False
