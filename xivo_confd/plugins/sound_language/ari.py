# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


class Client(object):

    def __init__(self, host='localhost', port=5039, https=False, username=None, password=None):
        self._host = host
        self._port = port
        self._https = https
        self._username = username
        self._password = password
        self._base_url = '{scheme}://{host}{port}/ari'.format(
            scheme='https' if self._https else 'http',
            host=self._host,
            port=':{}'.format(self._port) if self._port else ''
        )

    def get_sounds_languages(self):
        # TODO fetch value from asterisk
        return [{'tag': 'en_US'},
                {'tag': 'fr_FR'}]
