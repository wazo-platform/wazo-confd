# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests


class ARIClient(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def url(self, *parts):
        return 'http://{host}:{port}/{path}'.format(host=self.host,
                                                    port=self.port,
                                                    path='/'.join(parts))

    def set_sounds(self, sounds):
        url = self.url('_set_response')
        body = {'response': 'sounds',
                'content': sounds}
        requests.post(url, json=body)

    def set_sound(self, sound):
        url = self.url('_set_response')
        body = {'response': 'sounds/{}'.format(sound['id']),
                'content': sound}
        requests.post(url, json=body)

    def reset(self):
        url = self.url('_reset')
        requests.post(url)

    def requests(self):
        url = self.url('_requests')
        return requests.get(url).json()
