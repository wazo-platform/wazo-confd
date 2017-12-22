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

    def list_directories(self):
        try:
            directories = self._list_directories(self._base_path)
        except OSError as e:
            logger.error('Could not list sound directory %s: %s', self._base_path, e)
            raise

        directories.sort()
        return [self.get_directory(directory_name) for directory_name in directories]

    def _list_directories(self, path):
        return [name for name in os.listdir(path)
                if os.path.isdir(self._path(path, name))
                and name not in RESERVED_DIRECTORIES]

    def get_directory(self, sound_name):
        if sound_name in RESERVED_DIRECTORIES:
            raise errors.not_found('Sound', name=sound_name)
        sound = SoundCategory(name=sound_name)
        sound.files = self._list_sound_files(sound)
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

    def _list_sound_files(self, sound):
        path = self._directory_path(sound)
        try:
            directories, files = self._list_directories_files(path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise errors.not_found('Sound', name=sound.name)
            else:
                logger.error('Could not list sound directory %s: %s', path, e)
                return []

        result = {}
        self._extract_and_merge_formats(result, files)

        for directory in directories:
            path = self._path(path, directory)
            try:
                files = os.listdir(path)
            except OSError as e:
                logger.error('Could not list sound language directory %s: %s', path, e)
                continue

            self._extract_and_merge_formats(result, files, language=directory)

        return result.values()

    def _extract_and_merge_formats(self, result, files, language=None):
        for file_ in files:
            # XXX: convert extension to format (i.e. wav to slin)
            filename, extension = os.path.splitext(file_)
            extension = extension.strip('.') if extension else extension
            sound_file = result.setdefault(filename, SoundFile(filename))
            sound_file.formats.append(SoundFormat(format_=extension, language=language))
        return result

    def _list_directories_files(self, path):
        directories = []
        files = []
        for name in os.listdir(path):
            full_name = self._path(path, name)
            if os.path.isfile(full_name):
                files.append(name)
            elif os.path.isdir(full_name):
                directories.append(name)
        return directories, files

    def load_file(self, sound, filename):
        path = self._filename_path(sound, filename)
        if not os.path.isfile(path):
            raise errors.not_found('Sound file', name=sound.name, filename=filename)
        return send_file(path, mimetype='application/octet-stream')

    def save_file(self, sound, filename, content):
        path = self._filename_path(sound, filename)
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o660), 'wb') as fobj:
            return fobj.write(content)

    def remove_file(self, sound, filename):
        path = self._filename_path(sound, filename)
        try:
            os.remove(path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise errors.not_found('Sound file', name=sound.name, filename=filename)
            raise
