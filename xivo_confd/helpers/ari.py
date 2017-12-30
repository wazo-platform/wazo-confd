# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import re
import requests
from requests import RequestException

LANGUAGE_REGEX = r'^[a-zA-Z]{2,3}_[a-zA-Z]{2,3}$'


class AsteriskUnreachable(Exception):
    pass


class AsteriskUnauthorized(Exception):
    pass


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
        self._params = {'api_key': '{}:{}'.format(username, password)}

    def get_sounds(self, params=None):
        url = '{base_url}/sounds'.format(base_url=self._base_url)
        if params and 'language' in params:
            self._params['lang'] = params['language']
        if params and 'format' in params:
            self._params['format'] = params['format']
        try:
            response = requests.get(url, params=self._params)
        except RequestException as e:
            raise AsteriskUnreachable(e)

        if response.status_code == 401:
            raise AsteriskUnauthorized('Asterisk unauthorized error {}'.format(self._params))

        response.raise_for_status()
        return response.json()

    def get_sounds_languages(self):
        sounds = self.get_sounds()
        languages = self._extract_sounds_languages(sounds)
        sound_languages = [{'tag': language} for language in languages]
        sound_languages = self._remove_non_standard_tag(sound_languages)
        return sound_languages

    def _extract_sounds_languages(self, sounds):
        return set(format_['language'] for sound in sounds for format_ in sound['formats'])

    def _remove_non_standard_tag(self, languages):
        return [language for language in languages if re.match(LANGUAGE_REGEX, language['tag'])]
