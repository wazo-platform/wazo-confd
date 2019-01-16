# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re
import requests
from requests import RequestException, HTTPError

LANGUAGE_REGEX = r'^[a-zA-Z]{2,3}_[a-zA-Z]{2,3}$'


class AsteriskUnreachable(RequestException):
    pass


class AsteriskUnauthorized(HTTPError):
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

    def get_sounds(self):
        url = '{base_url}/sounds'.format(base_url=self._base_url)
        try:
            response = requests.get(url, params=self._params)
        except RequestException as e:
            raise AsteriskUnreachable(e)

        if response.status_code == 401:
            raise AsteriskUnauthorized('Asterisk unauthorized error {}'.format(self._params))

        response.raise_for_status()
        results = []
        for sound in response.json():
            result = self._remove_non_standard_language(sound)
            if result['formats']:
                results.append(result)
        return results

    def _remove_non_standard_language(self, sound):
        result = dict(sound)
        result['formats'] = []

        for format_ in sound['formats']:
            if format_['language'] and not re.match(LANGUAGE_REGEX, format_['language']):
                continue
            result['formats'].append(format_)

        return result

    def get_sound(self, sound_id, params=None):
        params = params or {}
        url = '{base_url}/sounds/{sound_id}'.format(base_url=self._base_url, sound_id=sound_id)
        try:
            response = requests.get(url, params=self._params)
        except RequestException as e:
            raise AsteriskUnreachable(e)

        if response.status_code == 401:
            raise AsteriskUnauthorized('Asterisk unauthorized error {}'.format(self._params))

        response.raise_for_status()
        result = self._filter_sound(response.json(), params)
        result = self._remove_non_standard_language(result)
        return result

    def _filter_sound(self, sound, parameters):
        format_filter = parameters.get('format')
        language_filter = parameters.get('language')
        formats_filtered = []
        for format_ in sound.get('formats'):
            if format_filter and format_filter != format_.get('format'):
                continue
            if language_filter and language_filter != format_.get('language'):
                continue
            formats_filtered.append(format_)
        sound['formats'] = formats_filtered
        return sound

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
