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

    def _directory_path(self, sound):
        return os.path.join(self._base_path, sound.name.encode('utf-8'))

    def _filename_path(self, sound, filename):
        return os.path.join(self._base_path, sound.name.encode('utf-8'), filename.encode('utf-8'))

    def _path(self, base_path, path):
        return os.path.join(base_path, path.encode('utf-8'))

    def list_directories(self, parameters):
        try:
            directories = self._list_directories(self._base_path)
        except OSError as e:
            logger.error('Could not list sound directory %s: %s', self._base_path, e)
            raise

        directories.sort()
        return [self.get_directory(directory_name, parameters) for directory_name in directories]

    def _list_directories(self, path):
        return [name for name in os.listdir(path)
                if os.path.isdir(self._path(path, name))
                and name not in RESERVED_DIRECTORIES]

    def get_directory(self, sound_name, parameters):
        if sound_name in RESERVED_DIRECTORIES:
            raise errors.not_found('Sound', name=sound_name)
        sound = SoundCategory(name=sound_name)
        sound = self._populate_files(sound, parameters)
        return sound

    def create_directory(self, sound):
        path = self._directory_path(sound)
        try:
            os.mkdir(path, 0o775)
        except OSError as e:
            if e.errno == errno.EEXIST:
                raise errors.resource_exists(sound, name=sound.name)
            else:
                logger.error('Could not create sound directory %s: %s', path, e)

    def remove_directory(self, sound):
        path = self._directory_path(sound)
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
        path = self._directory_path(sound)
        try:

            for file_ in os.listdir(path):
                full_name = self._path(path, file_)
                if os.path.isfile(full_name):
                    sound_file = self._create_sound_file(file_)
                    sound.add_file(sound_file)

                elif os.path.isdir(full_name):
                    if file_ != parameters.get('language', file_):
                        continue

                    try:
                        for lang_file in os.listdir(full_name):
                            sound_file = self._create_sound_file(lang_file, language=file_)
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

    def _create_sound_file(self, filename_ext, language=None):
        filename, extension = os.path.splitext(filename_ext)
        formats = [self._create_sound_format(extension, language)]
        return SoundFile(name=filename, formats=formats)

    def _create_sound_format(self, extension, language):
        format_ = extension.strip('.') if extension else extension
        return SoundFormat(format_=format_, language=language)

    def load_file(self, sound):
        filename = self._get_first_filename(sound)
        path = self._filename_path(sound, filename)
        if not os.path.isfile(path):
            raise errors.not_found('Sound file', name=sound.name, filename=filename)
        return send_file(path, mimetype='application/octet-stream')

    def save_file(self, sound, content):
        filename = self._get_first_filename(sound)
        path = self._filename_path(sound, filename)
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o660), 'wb') as fobj:
            return fobj.write(content)

    def remove_file(self, sound):
        filename = self._get_first_filename(sound)
        path = self._filename_path(sound, filename)
        try:
            os.remove(path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise errors.not_found('Sound file', name=sound.name, filename=filename)
            raise

    def _get_first_filename(self, sound):
        if not sound.files or not sound.files[0].formats:
            raise errors.not_found('Sound file', name=sound.name)

        # XXX change directory according to the language
        filename = "{}.{}".format(sound.files[0].name, sound.files[0].formats[0].format)
        return filename
