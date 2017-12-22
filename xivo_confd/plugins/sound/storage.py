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

DEFAULT_FOLDERS = ['acd', 'features', 'playback', 'recordings']
RESERVED_FOLDERS = ['monitor', 'recordings-meetme']


def build_storage(base_path='/var/lib/xivo/sounds'):
    return _SoundFilesystemStorage(base_path)


class _SoundFilesystemStorage(object):

    def __init__(self, base_path):
        self._base_path = base_path

    def _directory_path(self, sound):
        return os.path.join(self._base_path, sound.name.encode('utf-8'))

    def _filename_path(self, sound, filename):
        return os.path.join(self._base_path, sound.name.encode('utf-8'), filename.encode('utf-8'))

    def list_directories(self):
        try:
            folders = self._list_directories(self._base_path)
        except OSError as e:
            logger.error('Could not list sound directory %s: %s', self._base_path, e)
            raise e

        folders = [folder for folder in folders if folder not in RESERVED_FOLDERS]
        return [self.get_directory(folder) for folder in folders]

    def _list_directories(path):
        # Valid with a symlink -> directory
        return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

    def get_directory(self, sound_name):
        if sound_name in RESERVED_FOLDERS:
            raise errors.not_found('Sound', name=sound_name)
        sound = SoundCategory(name=sound_name)
        sound.files = self._list_files(sound)
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

    def _list_files(self, sound):
        path = self._directory_path(sound)
        try:
            filenames = os.listdir(path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise errors.not_found('Sound', name=sound.name)
            else:
                logger.error('Could not list sound directory %s: %s', path, e)
            filenames = []
        filenames.sort()
        # we currently returns the whole list of files in the directory, even if they
        # aren't file (e.g. directory) or they have an invalid filename (e.g. a filename
        # that confd won't accept) for simplicity

        # XXX Extract format
        # XXX consider all subfolder as language folder
        # XXX separe folder and file
        files = [SoundFile(name=filename) for filename in filenames]
        return files

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
            raise e
