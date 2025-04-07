# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import errno
import glob
import logging
import os
import shutil
from contextlib import contextmanager

from flask import send_file
from xivo_dao.helpers import errors

from .model import SoundCategory, SoundFile, SoundFormat

logger = logging.getLogger(__name__)

DEFAULT_DIRECTORIES = ['acd', 'features', 'playback', 'recordings']
RESERVED_DIRECTORIES = ['monitor', 'recordings-meetme']


def build_storage(base_path='/var/lib/wazo/sounds'):
    return _SoundFilesystemStorage(base_path)


class _SoundFilesystemStorage:
    def __init__(self, base_path):
        self._base_path = base_path

    def _build_path(self, *fragments):
        fragments = [fragment for fragment in fragments if fragment]

        dangerous_fragments = [
            fragment for fragment in fragments if '..' in fragment or '/' in fragment
        ]
        if dangerous_fragments:
            raise errors.not_permitted(
                'Dangerous path fragment: "{}"'.format(dangerous_fragments)
            )

        return os.path.join(self._base_path, *fragments)

    def list_directories(self, parameters, tenant_uuids):
        result = []
        for tenant_uuid in tenant_uuids:
            try:
                directories = self._list_directories(tenant_uuid)
            except OSError as e:
                logger.error(
                    'Could not list sound directory %s/tenants/%s: %s',
                    self._base_path,
                    tenant_uuid,
                    e,
                )
                continue

            directories.sort()
            logger.debug('Found directories: %s', directories)
            result.extend(
                [
                    self.get_directory(tenant_uuid, directory_name, parameters)
                    for directory_name in directories
                ]
            )

        return result

    def _list_directories(self, tenant_uuid):
        return [
            name
            for name in os.listdir(self._build_path('tenants', tenant_uuid))
            if os.path.isdir(self._build_path('tenants', tenant_uuid, name))
            and name not in RESERVED_DIRECTORIES
        ]

    def get_directory(self, tenant_uuid, directory, parameters, with_files=True):
        if directory in RESERVED_DIRECTORIES:
            raise errors.not_found('Sound', name=directory)

        if not os.path.exists(self._build_path('tenants', tenant_uuid, directory)):
            raise errors.not_found('Sound', name=directory, **parameters)

        sound = SoundCategory(name=directory, tenant_uuid=tenant_uuid)

        if with_files:
            sound = self._populate_files(sound, parameters)
        return sound

    def create_directory(self, sound):
        path = self._build_path('tenants', sound.tenant_uuid, sound.name)
        with umask_disabled():
            try:
                os.makedirs(path, 0o775)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    raise errors.resource_exists(sound, name=sound.name)
                else:
                    logger.error('Could not create sound directory %s: %s', path, e)

    def remove_directory(self, sound):
        path = self._build_path('tenants', sound.tenant_uuid, sound.name)
        try:
            shutil.rmtree(path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.info('Sound directory %s already removed', path)
            else:
                logger.error('Could not remove sound directory %s: %s', path, e)

    def _populate_files(self, sound, parameters):
        language_filter = parameters.get('language')
        format_filter = parameters.get('format')
        filename_filter = parameters.get('file_name')

        if filename_filter and language_filter and format_filter:
            return self._filter_filename_language_format(
                sound, filename_filter, language_filter, format_filter
            )

        elif filename_filter and language_filter:
            return self._filter_filename_language(
                sound, filename_filter, language_filter
            )

        elif filename_filter and format_filter:
            return self._filter_filename_format(sound, filename_filter, format_filter)

        elif filename_filter:
            return self._filter_filename(sound, filename_filter)

        elif language_filter and format_filter:
            return self._filter_language_format(sound, language_filter, format_filter)

        elif language_filter:
            return self._filter_language(sound, language_filter)

        elif format_filter:
            return self._filter_format(sound, format_filter)

        else:
            return self._filter_none(sound)

    def _filter_filename_language_format(
        self, sound, filename_filter, language_filter, format_filter
    ):
        filename_extension = '{}.{}'.format(
            filename_filter, SoundFormat(format_filter).extension
        )
        path = self._build_path(
            'tenants',
            sound.tenant_uuid,
            sound.name,
            language_filter,
            filename_extension,
        )
        sound = self._find_and_populate_sound(sound, path, extract_language=True)
        return sound

    def _filter_filename_language(self, sound, filename_filter, language_filter):
        path = self._build_path(
            'tenants', sound.tenant_uuid, sound.name, language_filter, filename_filter
        )
        sound = self._find_and_populate_sound(sound, path, extract_language=True)

        filename_extension = '{}.*'.format(filename_filter)
        path = self._build_path(
            'tenants',
            sound.tenant_uuid,
            sound.name,
            language_filter,
            filename_extension,
        )
        sound = self._find_and_populate_sound(sound, path, extract_language=True)

        return sound

    def _filter_filename_format(self, sound, filename_filter, format_filter):
        filename_extension = '{}.{}'.format(
            filename_filter, SoundFormat(format_filter).extension
        )

        path = self._build_path(
            'tenants', sound.tenant_uuid, sound.name, filename_extension
        )
        sound = self._find_and_populate_sound(sound, path)

        path = self._build_path(
            'tenants', sound.tenant_uuid, sound.name, '*', filename_extension
        )
        sound = self._find_and_populate_sound(sound, path, extract_language=True)

        return sound

    def _filter_filename(self, sound, filename_filter):
        path = self._build_path(
            'tenants', sound.tenant_uuid, sound.name, filename_filter
        )
        sound = self._find_and_populate_sound(sound, path)

        path = self._build_path(
            'tenants', sound.tenant_uuid, sound.name, '*', filename_filter
        )
        sound = self._find_and_populate_sound(sound, path, extract_language=True)

        filename_extension = '{}.*'.format(filename_filter)
        path = self._build_path(
            'tenants', sound.tenant_uuid, sound.name, filename_extension
        )
        sound = self._find_and_populate_sound(sound, path)

        path = self._build_path(
            'tenants', sound.tenant_uuid, sound.name, '*', filename_extension
        )
        sound = self._find_and_populate_sound(sound, path, extract_language=True)

        return sound

    def _filter_language_format(self, sound, language_filter, format_filter):
        filename_extension = '*.{}'.format(SoundFormat(format_=format_filter).extension)
        path = self._build_path(
            'tenants',
            sound.tenant_uuid,
            sound.name,
            language_filter,
            filename_extension,
        )
        sound = self._find_and_populate_sound(sound, path, extract_language=True)
        return sound

    def _filter_language(self, sound, language_filter):
        path = self._build_path(
            'tenants', sound.tenant_uuid, sound.name, language_filter, '*'
        )
        sound = self._find_and_populate_sound(sound, path, extract_language=True)
        return sound

    def _filter_format(self, sound, format_filter):
        filename_extension = '*.{}'.format(SoundFormat(format_=format_filter).extension)

        path = self._build_path(
            'tenants', sound.tenant_uuid, sound.name, filename_extension
        )
        sound = self._find_and_populate_sound(sound, path)

        path = self._build_path(
            'tenants', sound.tenant_uuid, sound.name, '*', filename_extension
        )
        sound = self._find_and_populate_sound(sound, path, extract_language=True)

        return sound

    def _filter_none(self, sound):
        path = self._build_path('tenants', sound.tenant_uuid, sound.name, '*')
        sound = self._find_and_populate_sound(sound, path)

        path = self._build_path('tenants', sound.tenant_uuid, sound.name, '*', '*')
        sound = self._find_and_populate_sound(sound, path, extract_language=True)

        return sound

    def _find_and_populate_sound(self, sound, path, extract_language=False):
        for file_ in glob.glob(path):
            if not os.path.isfile(file_):
                continue
            sound_file = self._create_sound_file(
                sound.tenant_uuid, file_, extract_language=extract_language
            )
            sound.add_file(sound_file)
        return sound

    def _create_sound_file(self, tenant_uuid, path, extract_language=False):
        language = None
        if extract_language:
            language = os.path.basename(os.path.dirname(path))
        basename = os.path.basename(path)
        filename, extension = os.path.splitext(basename)
        extension = extension.strip('.') if extension else extension
        path_without_extension = os.path.join(os.path.dirname(path), filename)
        sound_format = SoundFormat(
            tenant_uuid=tenant_uuid,
            language=language,
            path=path_without_extension,
            extension=extension,
        )
        return SoundFile(tenant_uuid=tenant_uuid, name=filename, formats=[sound_format])

    def load_first_file(self, sound):
        path = self._get_first_file_path(sound)
        if not os.path.isfile(path):
            raise errors.not_found('Sound file', name=sound.name, path=path)
        return send_file(path, mimetype='application/octet-stream', as_attachment=True)

    def save_first_file(self, sound, content):
        path = self._get_first_file_path(sound)
        self._ensure_directory(os.path.dirname(path))
        with os.fdopen(
            os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o660), 'wb'
        ) as fobj:
            return fobj.write(content)

    def remove_files(self, sound):
        paths = self._get_file_paths(sound)
        remove_errors = []
        for path in paths:
            try:
                os.remove(path)
            except OSError as e:
                if e.errno == errno.ENOENT:
                    remove_errors.append(
                        errors.not_found('Sound file', name=sound.name, path=path)
                    )
                else:
                    remove_errors.append(e)

        if len(remove_errors) == len(paths):
            for error in remove_errors:
                raise error

    def _get_first_file_path(self, sound):
        paths = self._get_file_paths(sound)
        paths = self._sort_without_language_first(paths)
        for path in paths:
            return path
        raise errors.not_found('Sound file', name=sound.name)

    def _sort_without_language_first(self, paths):
        # We cannot set format/language to None in the query
        # string when getting file.
        # example:
        #   * /path/category/toto.wav
        #   * /path/category/fr_FR/toto.wav
        #
        # to get the first toto.wav, we need to sort list before
        # returning the first_file_path
        paths.sort(key=len)
        return paths

    def _get_file_paths(self, sound):
        for file_ in sound.files:
            if sound.tenant_uuid:
                return [
                    '{}{}'.format(
                        self._build_path(
                            'tenants',
                            sound.tenant_uuid,
                            sound.name,
                            format_.language,
                            file_.name,
                        ),
                        '.{}'.format(format_.extension) if format_.extension else '',
                    )
                    for format_ in file_.formats
                ]
            else:
                return [
                    '{}{}'.format(
                        self._build_path(sound.name, format_.language, file_.name),
                        '.{}'.format(format_.extension) if format_.extension else '',
                    )
                    for format_ in file_.formats
                ]
        raise errors.not_found('Sound file', name=sound.name)

    def _ensure_directory(self, path):
        if not os.path.exists(path):
            with umask_disabled():
                try:
                    os.makedirs(path, 0o775)
                except OSError as e:
                    logger.error(
                        'Could not create sound language directory %s: %s', path, e
                    )
                    raise


@contextmanager
def umask_disabled():
    try:
        original_umask = os.umask(0)
        yield
    finally:
        os.umask(original_umask)
