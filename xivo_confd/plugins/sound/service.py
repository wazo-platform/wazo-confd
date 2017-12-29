# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .model import SoundCategory
from .notifier import build_notifier
from .schema import ASTERISK_CATEGORY
from .storage import build_storage
from .validator import build_validator, build_validator_file
from .converter import convert_ari_sounds_to_model


class SoundService(object):

    def __init__(self, ari_client, storage, asterisk_storage, validator, validator_file, notifier):
        self._ari_client = ari_client
        self._storage = storage
        self._asterisk_storage = asterisk_storage
        self.validator = validator
        self.validator_file = validator_file
        self.notifier = notifier

    def search(self, parameters):
        sound_system = self._get_asterisk_sound(parameters)
        sounds = self._storage.list_directories(parameters)
        sounds.append(sound_system)
        total = len(sounds)
        return total, sounds

    def get(self, sound_name, parameters=None, with_files=True):
        parameters = parameters if parameters is not None else {}
        if sound_name == ASTERISK_CATEGORY:
            sound = self._get_asterisk_sound(parameters, with_files)
        else:
            sound = self._storage.get_directory(sound_name, parameters, with_files)
        return sound

    def _get_asterisk_sound(self, parameters, with_files=True):
        sound = SoundCategory(name='system')
        if with_files:
            ari_sounds = self._ari_client.get_sounds(parameters)
            sound.files = convert_ari_sounds_to_model(ari_sounds)
        return sound

    def create(self, sound):
        self._storage.create_directory(sound)
        self.notifier.created(sound)
        return sound

    def delete(self, sound):
        self.validator.validate_delete(sound)
        self._storage.remove_directory(sound)
        self.notifier.deleted(sound)

    def load_first_file(self, sound):
        if sound.name == ASTERISK_CATEGORY:
            sound.name = ''
            sound = self._asterisk_storage.load_first_file(sound)
        else:
            sound = self._storage.load_first_file(sound)
        return sound

    def save_first_file(self, sound, content):
        self.validator_file.validate_edit(sound)
        self._storage.save_first_file(sound, content)

    def delete_files(self, sound):
        self.validator_file.validate_delete(sound)
        self._storage.remove_files(sound)


def build_service(ari_client):
    return SoundService(ari_client,
                        build_storage(),
                        build_storage(base_path='/usr/share/asterisk/sounds'),
                        build_validator(),
                        build_validator_file(),
                        build_notifier())
