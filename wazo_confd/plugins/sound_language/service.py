# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class SoundLanguageService:
    def __init__(self, ari_client):
        self.ari_client = ari_client

    def search(self, parameters):
        result = self.ari_client.get_sounds_languages()
        return len(result), result


def build_service(ari_client):
    return SoundLanguageService(ari_client)
