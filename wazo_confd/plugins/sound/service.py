# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from requests import HTTPError
from xivo_dao.helpers import errors

from .converter import convert_ari_sounds_to_model
from .model import SoundCategory
from .notifier import build_notifier
from .schema import ASTERISK_CATEGORY
from .storage import build_storage
from .validator import build_validator, build_validator_file

logger = logging.getLogger(__name__)


class SoundService:
    DEFAULT_ORDER = 'name'
    CATEGORY_SORTABLE_FIELDS = (DEFAULT_ORDER,)

    def __init__(
        self, ari_client, storage, asterisk_storage, validator, validator_file, notifier
    ):
        self._ari_client = ari_client
        self._storage = storage
        self._asterisk_storage = asterisk_storage
        self.validator = validator
        self.validator_file = validator_file
        self.notifier = notifier

    def search(self, parameters, tenant_uuids):
        sound_system = self._get_asterisk_sound(parameters)
        sounds = self._storage.list_directories(parameters, tenant_uuids)
        sounds.append(sound_system)

        sounds = self._filter_and_sort_categories(sounds, parameters)
        total = len(sounds)
        return total, sounds

    def _validate_parameters(self, parameters):
        direction = parameters.get('direction')
        if direction not in ['asc', 'desc', None]:
            raise errors.invalid_direction()

        offset = parameters.get('offset', 0)
        limit = offset + parameters['limit'] if 'limit' in parameters else None
        search = parameters.get('search', None)
        order = parameters.get('order', self.DEFAULT_ORDER)
        reverse = direction == 'desc'
        return search, order, offset, limit, reverse

    def _filter_and_sort_categories(self, sounds, parameters):
        pattern, order, offset, limit, reverse = self._validate_parameters(parameters)
        results = sounds
        if pattern:
            results = list(filter(lambda category: pattern in category.name, results))

        if order not in self.CATEGORY_SORTABLE_FIELDS:
            raise errors.invalid_ordering(order)

        results = sorted(
            results,
            key=lambda category: getattr(category, order),
            reverse=reverse,
        )

        return results[offset:limit]

    def get(self, tenant_uuid, category, parameters=None, with_files=True):
        parameters = parameters if parameters is not None else {}
        if category == ASTERISK_CATEGORY:
            sound = self._get_asterisk_sound(parameters, with_files)
        else:
            sound = self._storage.get_directory(
                tenant_uuid, category, parameters, with_files
            )
        return sound

    def _get_asterisk_sound(self, parameters, with_files=True):
        sound = SoundCategory(name='system')
        if with_files:
            if 'file_name' in parameters:
                try:
                    ari_sounds = [
                        self._ari_client.get_sound(parameters['file_name'], parameters)
                    ]
                except HTTPError as e:
                    if e.response.status_code == 404:
                        raise errors.not_found(
                            'Sound', name='system', file_name=parameters['file_name']
                        )
                    raise
            else:
                ari_sounds = self._ari_client.get_sounds()

            sound.files = convert_ari_sounds_to_model(ari_sounds)
        return sound

    def create(self, sound):
        logger.debug('Creating %s', sound)
        self._storage.create_directory(sound)
        self.notifier.created(sound)
        return sound

    def delete(self, sound):
        self.validator.validate_delete(sound)
        self._storage.remove_directory(sound)
        self.notifier.deleted(sound)

    def load_first_file(self, sound):
        if sound.name == ASTERISK_CATEGORY:
            sound.name = None
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

    def fetch_relations(self, form):
        return form


def build_service(ari_client):
    return SoundService(
        ari_client,
        build_storage(),
        build_storage(base_path='/usr/share/asterisk/sounds'),
        build_validator(),
        build_validator_file(),
        build_notifier(),
    )
