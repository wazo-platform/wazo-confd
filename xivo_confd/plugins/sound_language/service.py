# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


class SoundLanguageService(object):

    def __init__(self, ari_client):
        self.ari_client = ari_client

    def search(self, parameters):
        result = self.ari_client.get_sounds_languages()
        return len(result), result


def build_service(ari_client_proxy):
    return SoundLanguageService(ari_client_proxy)


class ARIClientProxy(object):

    def __init__(self, ari_client, bus):
        self._ari_client = ari_client
        self._bus = bus
        self._sounds_languages = []

    # TODO: On bus event (plugin installed), clear get_sounds_languages

    def get_sounds_languages(self):
        if not self._sounds_languages:
            sounds = self._ari_client.get_sounds_languages()
            languages = self._extract_sounds_languages(sounds)
            self._sounds_languages = [{'tag': language} for language in languages]
        return self._sounds_languages

    def _extract_sounds_languages(self, sounds):
        return set(format_['language'] for sound in sounds for format_ in sound['formats'])


def build_ari_client_proxy(ari_client, bus):
    return ARIClientProxy(ari_client, bus)
