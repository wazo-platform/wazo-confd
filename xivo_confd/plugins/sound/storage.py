# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import errno
import logging
import os.path
import shutil

from flask import send_file
from xivo_dao.helpers import errors

from .model import SoundCategory, SoundFormat, SoundFile

logger = logging.getLogger(__name__)

DEFAULT_DIRECTORIES = ['acd', 'features', 'playback', 'recordings']
RESERVED_DIRECTORIES = ['monitor', 'recordings-meetme']


def build_storage(base_path='/var/lib/xivo/sounds'):
    return _SoundFilesystemStorage(base_path)


class _SoundFilesystemStorage(object):

    def __init__(self, base_path):
        self._base_path = base_path

    def _build_path(self, *fragments):
        return os.path.join(self._base_path, *[fragment.encode('utf-8') for fragment in fragments if fragment])

    def list_directories(self, parameters):
        try:
            directories = self._list_directories()
        except OSError as e:
            logger.error('Could not list sound directory %s: %s', self._base_path, e)
            raise

        directories.sort()
        return [self.get_directory(directory_name, parameters) for directory_name in directories]

    def _list_directories(self):
        return [name for name in os.listdir(self._base_path)
                if os.path.isdir(self._build_path(name))
                and name not in RESERVED_DIRECTORIES]

    def get_directory(self, sound_name, parameters):
        if sound_name in RESERVED_DIRECTORIES:
            raise errors.not_found('Sound', name=sound_name)
        sound = SoundCategory(name=sound_name)
        sound = self._populate_files(sound, parameters)
        return sound

    def create_directory(self, sound):
        path = self._build_path(sound.name)
        try:
            os.mkdir(path, 0o775)
        except OSError as e:
            if e.errno == errno.EEXIST:
                raise errors.resource_exists(sound, name=sound.name)
            else:
                logger.error('Could not create sound directory %s: %s', path, e)

    def remove_directory(self, sound):
        path = self._build_path(sound.name)
        try:
            shutil.rmtree(path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.info('Sound directory %s already removed', path)
            else:
                logger.error('Could not remove sound directory %s: %s', e)

    def _populate_files(self, sound, parameters):
        # XXX Can be improved by doing only the right request when parameters is set
        #     And probably with other module (e.i. glob) for pattern matching
        path = self._build_path(sound.name)
        logger.critical(path)
        try:

            for file_ in os.listdir(path):
                full_name = self._build_path(sound.name, file_)
                if os.path.isfile(full_name):
                    sound_file = self._create_sound_file(file_)
                    sound.add_file(sound_file)

                elif os.path.isdir(full_name):
                    if file_ != parameters.get('language', file_):
                        continue

                    try:
                        for lang_file in os.listdir(full_name):
                            sound_file = self._create_sound_file(lang_file, language=file_, category=sound.name)
                            sound.add_file(sound_file)
                    except OSError as e:
                        logger.error('Could not list sound language directory %s: %s', full_name, e)
                        continue

        except OSError as e:
            if e.errno == errno.ENOENT:
                raise errors.not_found('Sound', name=sound.name, **parameters)
            else:
                logger.error('Could not list sound directory %s: %s', path, e)
                return []

        return self._filter(sound, parameters)

    def _filter(self, sound, parameters):
        files_filtered = []
        for file_ in sound.files:
            if file_.name != parameters.get('file_name', file_.name):
                continue
            formats_filtered = []
            for format_ in file_.formats:
                if format_.format != parameters.get('format', format_.format):
                    continue
                if format_.language != parameters.get('language', format_.language):
                    continue
                formats_filtered.append(format_)
            file_.formats = formats_filtered
            files_filtered.append(file_)
        sound.files = files_filtered
        return sound

    def _create_sound_file(self, filename_ext, language=None, category=None):
        filename, extension = os.path.splitext(filename_ext)
        format_ = extension.strip('.') if extension else extension
        path = self._build_path(category, language, filename)
        sound_format = SoundFormat(format_=format_, language=language, path=path)
        return SoundFile(name=filename, formats=[sound_format])

    def load_first_file(self, sound):
        path = self._get_first_file_path(sound)
        if not os.path.isfile(path):
            raise errors.not_found('Sound file', name=sound.name, path=path)
        return send_file(path, mimetype='application/octet-stream')

    def save_first_file(self, sound, content):
        path = self._get_first_file_path(sound)
        self._ensure_directory(os.path.dirname(path))
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o660), 'wb') as fobj:
            return fobj.write(content)

    def remove_files(self, sound):
        paths = self._get_file_paths(sound)
        try:
            for path in paths:
                os.remove(path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise errors.not_found('Sound file', name=sound.name, path=path)
            raise

    def _get_first_file_path(self, sound):
        for path in self._get_file_paths(sound):
            return path
        raise errors.not_found('Sound file', name=sound.name)

    def _get_file_paths(self, sound):
        for file_ in sound.files:
            return ['{}.{}'.format(
                self._build_path(sound.name, format_.language, file_.name),
                format_.format,
            ) for format_ in file_.formats]
        raise errors.not_found('Sound file', name=sound.name)

    def _ensure_directory(self, path):
        if not os.path.exists(path):
            try:
                os.mkdir(path, 0o775)
            except OSError as e:
                logger.error('Could not create sound language directory %s: %s', path, e)
                raise
