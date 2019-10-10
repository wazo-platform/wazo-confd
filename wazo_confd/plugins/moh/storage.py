# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import errno
import logging
import os.path
import shutil

from flask import send_file
from xivo_dao.helpers import errors

logger = logging.getLogger(__name__)


def build_storage(base_path='/var/lib/asterisk/moh'):
    return _MohFilesystemStorage(base_path)


class _MohFilesystemStorage:
    def __init__(self, base_path):
        self._base_path = base_path

    def _directory_path(self, moh):
        return os.path.join(self._base_path, moh.name)

    def _filename_path(self, moh, filename):
        return os.path.join(self._base_path, moh.name, filename)

    def create_directory(self, moh):
        path = self._directory_path(moh)
        try:
            os.mkdir(path, 0o775)
        except OSError as e:
            if e.errno == errno.EEXIST:
                if os.path.isdir(path):
                    logger.info('MOH directory %s already exist', path)
                else:
                    logger.error(
                        'Could not create MOH directory %s: file exists and is not a directory',
                        path,
                    )
            else:
                logger.error('Could not create MOH directory %s: %s', path, e)

    def remove_directory(self, moh):
        path = self._directory_path(moh)
        try:
            shutil.rmtree(path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.info('MOH directory %s already removed', path)
            else:
                logger.error('Could not remove MOH directory %s: %s', path, e)

    def list_files(self, moh):
        path = self._directory_path(moh)
        try:
            filenames = os.listdir(path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.info('MOH directory %s doesn\'t exist', path)
            else:
                logger.error('Could not list MOH directory %s: %s', path, e)
            filenames = []
        filenames.sort()
        # we currently returns the whole list of files in the directory, even if they
        # aren't file (e.g. directory) or they have an invalid filename (e.g. a filename
        # that confd won't accept) for simplicity
        return [{'name': filename} for filename in filenames]

    def load_file(self, moh, filename):
        path = self._filename_path(moh, filename)
        if not os.path.isfile(path):
            raise _moh_file_not_found(path, moh, filename)
        return send_file(path, mimetype='application/octet-stream', as_attachment=True)

    def save_file(self, moh, filename, content):
        path = self._filename_path(moh, filename)
        with os.fdopen(
            os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o660), 'wb'
        ) as fobj:
            return fobj.write(content)

    def remove_file(self, moh, filename):
        path = self._filename_path(moh, filename)
        try:
            os.remove(path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise _moh_file_not_found(path, moh, filename)
            raise


def _moh_file_not_found(path, moh, filename):
    logger.info('MOH file %s not found', path)
    raise errors.not_found('MOH file', uuid=moh.uuid, filename=filename)
