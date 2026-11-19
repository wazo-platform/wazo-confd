# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from unittest.mock import patch

import pytest

from ..config import (
    DEFAULT_CONFIG,
    VALID_ROLES,
    _normalize_roles,
    _parse_cli_args,
    load,
)


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


def test_default_config_roles():
    assert DEFAULT_CONFIG['roles'] == {'api': True, 'consumer': True}
    assert VALID_ROLES == ('api', 'consumer')


def test_cli_role_disables_the_others():
    result = _parse_cli_args(['--role', 'api'])

    assert result['roles'] == {'api': True, 'consumer': False}


def test_cli_role_is_repeatable():
    result = _parse_cli_args(['--role', 'api', '--role', 'consumer'])

    assert result['roles'] == {'api': True, 'consumer': True}


def test_cli_unknown_role_is_rejected():
    with pytest.raises(SystemExit):
        _parse_cli_args(['--role', 'bogus'])


def test_normalize_roles_keeps_enabled_roles_sorted():
    assert _normalize_roles({'consumer': True, 'api': True}) == ['api', 'consumer']
    assert _normalize_roles({'consumer': False, 'api': True}) == ['api']


def test_normalize_roles_rejects_unknown_role():
    with pytest.raises(ValueError):
        _normalize_roles({'api': True, 'bogus': True})


def test_normalize_roles_rejects_all_roles_disabled():
    with pytest.raises(ValueError):
        _normalize_roles({'api': False, 'consumer': False})


def test_normalize_roles_rejects_a_list():
    with pytest.raises(ValueError):
        _normalize_roles(['api'])


def test_load_enables_every_role_by_default(config_files):
    config = load([])

    assert config['roles'] == ['api', 'consumer']


def test_load_merges_a_role_disabled_in_a_file(config_files):
    config_files.return_value = {'roles': {'consumer': False}}

    config = load([])

    assert config['roles'] == ['api']


def test_load_cli_role_overrides_the_files(config_files):
    config_files.return_value = {'roles': {'api': False}}

    config = load(['--role', 'api'])

    assert config['roles'] == ['api']


def test_load_rejects_every_role_disabled(config_files):
    config_files.return_value = {'roles': {'api': False, 'consumer': False}}

    with pytest.raises(ValueError):
        load([])


def test_cli_listen_port_sets_the_rest_api_port():
    result = _parse_cli_args(['--listen-port', '19486'])

    assert result['rest_api'] == {'port': 19486}


def test_cli_listen_port_and_profile_are_both_kept():
    result = _parse_cli_args(['--listen-port', '19486', '--profile', '/tmp/profile'])

    assert result['rest_api'] == {'port': 19486, 'profile': '/tmp/profile'}


def test_cli_no_listen_port_leaves_rest_api_unset():
    result = _parse_cli_args([])

    assert 'rest_api' not in result


def test_load_cli_listen_port_overrides_file_port_but_keeps_listen(config_files):
    config_files.return_value = {'rest_api': {'port': 9486, 'listen': '0.0.0.0'}}

    config = load(['--listen-port', '19486'])

    assert config['rest_api']['port'] == 19486
    assert config['rest_api']['listen'] == '0.0.0.0'


def test_load_advertise_port_defaults_to_the_rest_api_port(config_files):
    config = load([])

    assert config['service_discovery']['advertise_port'] == 9486
    assert config['service_discovery']['advertise_address'] == 'auto'


def test_load_advertise_port_follows_the_cli_port(config_files):
    config = load(['--listen-port', '19486'])

    assert config['service_discovery']['advertise_port'] == 19486


def test_load_explicit_advertise_port_is_respected(config_files):
    config_files.return_value = {
        'rest_api': {'port': 9600},
        'service_discovery': {'advertise_port': 12345},
    }

    config = load([])

    assert config['service_discovery']['advertise_port'] == 12345
