# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from unittest.mock import patch

import pytest

from ..config import _parse_cli_args, load


@pytest.fixture
def config_files():
    with (
        patch('wazo_confd.config.read_config_file_hierarchy') as read_config_files,
        patch('wazo_confd.config.parse_config_file') as parse_key_file,
    ):
        read_config_files.return_value = {}
        parse_key_file.return_value = {'service_id': 'id', 'service_key': 'key'}
        yield read_config_files


def test_cli_no_args_only_sets_the_log_level():
    result = _parse_cli_args([])

    assert result == {'log_level': 'INFO'}


def test_cli_profile_sets_the_rest_api_profile():
    result = _parse_cli_args(['--profile', '/tmp/profile'])

    assert result['rest_api'] == {'profile': '/tmp/profile'}


def test_load_uses_the_defaults(config_files):
    config = load([])

    assert config['rest_api']['port'] == 9486
    assert config['log_level'] == logging.INFO


def test_load_file_overrides_a_default_but_keeps_its_siblings(config_files):
    config_files.return_value = {'rest_api': {'port': 9600}}

    config = load([])

    assert config['rest_api']['port'] == 9600
    assert config['rest_api']['listen'] == '127.0.0.1'


def test_load_cli_overrides_the_files(config_files):
    config_files.return_value = {'user': 'from-file'}

    config = load(['--user', 'from-cli'])

    assert config['user'] == 'from-cli'


def test_load_reads_the_credentials_from_the_key_file(config_files):
    config = load([])

    assert config['auth']['username'] == 'id'
    assert config['auth']['password'] == 'key'
    assert config['auth']['host'] == 'localhost'


def test_load_keeps_the_configured_credentials(config_files):
    config_files.return_value = {'auth': {'username': 'user', 'password': 'secret'}}

    config = load([])

    assert config['auth']['username'] == 'user'
    assert config['auth']['password'] == 'secret'


def test_load_rejects_an_unknown_log_level(config_files):
    with pytest.raises(ValueError):
        load(['--log-level', 'bogus'])
