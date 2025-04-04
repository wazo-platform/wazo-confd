# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re
from contextlib import contextmanager

from hamcrest import (
    assert_that,
    has_entries,
    has_entry,
    has_item,
    has_key,
    is_not,
    none,
)

from ..helpers import associations as a
from ..helpers import fixtures
from ..helpers import helpers as h
from ..helpers import scenarios as s
from ..helpers.config import TOKEN_SUB_TENANT
from ..helpers.helpers.line_fellowship import line_fellowship
from . import confd, provd


@contextmanager
def line_device(endpoint_type='sip', registrar=None):
    device = h.device.generate_device()

    line_etc = line_fellowship(endpoint_type=endpoint_type, registrar=registrar)
    with line_etc as (user, line, extension, endpoint):
        with a.line_device(line, device):
            yield line, device

    h.device.delete_device(device['id'])


def test_search_errors():
    url = confd.registrars.get
    s.search_error_checks(url)


def test_get_errors():
    fake_get = confd.registrars(999999).get
    s.check_resource_not_found(fake_get, 'Registrar')


def test_post_errors():
    url = confd.registrars.post
    error_checks(url)


@fixtures.registrar()
def test_put_errors(registrar):
    url = confd.registrars(registrar['id']).put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'main_host', None)
    s.check_bogus_field_returns_error(url, 'deletable', 123)
    s.check_bogus_field_returns_error(url, 'deletable', 'wrong')
    s.check_bogus_field_returns_error(url, 'main_host', 123)
    s.check_bogus_field_returns_error(url, 'main_port', 'wrong')
    s.check_bogus_field_returns_error(url, 'backup_host', 123)
    s.check_bogus_field_returns_error(url, 'backup_port', 'wrong')
    s.check_bogus_field_returns_error(url, 'proxy_main_host', None)
    s.check_bogus_field_returns_error(url, 'proxy_main_host', 123)
    s.check_bogus_field_returns_error(url, 'proxy_main_port', 'wrong')
    s.check_bogus_field_returns_error(url, 'proxy_backup_host', 123)
    s.check_bogus_field_returns_error(url, 'proxy_backup_port', 'wrong')
    s.check_bogus_field_returns_error(url, 'outbound_proxy_host', 123)
    s.check_bogus_field_returns_error(url, 'outbound_proxy_port', 'wrong')


@fixtures.registrar(
    id='VisibleId',
    name='VisibleRegistrar',
    proxy_main_host='1.2.3.4',
    outbound_proxy_port=5060,
)
@fixtures.registrar(
    id='HiddenId',
    name='HiddenRegistrar',
    proxy_main_host='1.2.2.4',
    outbound_proxy_port=5061,
)
def test_search(registrar, hidden):
    url = confd.registrars
    searches = {
        'proxy_main_host': '1.2.3',
        'id': 'leid',
        'name': 'ereg',
        'outbound_proxy_port': 5060,
    }

    for field, term in searches.items():
        check_search(url, registrar, hidden, field, term)


def check_search(url, registrar, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, registrar[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: registrar[field]})
    assert_that(response.items, has_item(has_entry('id', registrar['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.registrar(
    proxy_main_host="99.20.30.40", name="SortRegistrar1", main_port=5060
)
@fixtures.registrar(
    proxy_main_host="99.20.30.50", name="SortRegistrar2", main_port=5061
)
def test_sorting_offset_limit(registrar1, registrar2):
    url = confd.registrars.get
    s.check_sorting(url, registrar1, registrar2, 'proxy_main_host', '99.20.30.')
    s.check_sorting(url, registrar1, registrar2, 'name', 'SortRegistrar')
    s.check_sorting(url, registrar1, registrar2, 'main_port', 'SortRegistrar')

    s.check_offset(url, registrar1, registrar2, 'name', 'Sort')
    s.check_limit(url, registrar1, registrar2, 'name', 'Sort')


@fixtures.registrar()
def test_get(registrar):
    response = confd.registrars(registrar['id']).get()
    assert_that(response.item, has_entries(**registrar))


def test_create_registrar_minimal_parameters():
    response = confd.registrars.post(main_host='1.2.3.4', proxy_main_host='1.2.3.4')
    response.assert_created('registrars')

    assert_that(
        response.item,
        has_entries(
            deletable=True,
            name=none(),
            main_host='1.2.3.4',
            main_port=none(),
            backup_host=none(),
            backup_port=none(),
            proxy_main_host='1.2.3.4',
            proxy_main_port=none(),
            proxy_backup_host=none(),
            proxy_backup_port=none(),
            outbound_proxy_host=none(),
            outbound_proxy_port=none(),
        ),
    )


def test_create_registrar_null_parameters():
    response = confd.registrars.post(
        deletable=True,
        name=None,
        main_host='1.2.3.4',
        main_port=None,
        backup_host=None,
        backup_port=None,
        proxy_main_host='1.2.3.4',
        proxy_main_port=None,
        proxy_backup_host=None,
        proxy_backup_port=None,
        outbound_proxy_host=None,
        outbound_proxy_port=None,
    )
    response.assert_created('registrars')

    assert_that(
        response.item,
        has_entries(
            deletable=True,
            name=none(),
            main_host='1.2.3.4',
            main_port=none(),
            backup_host=none(),
            backup_port=none(),
            proxy_main_host='1.2.3.4',
            proxy_main_port=none(),
            proxy_backup_host=none(),
            proxy_backup_port=none(),
            outbound_proxy_host=none(),
            outbound_proxy_port=none(),
        ),
    )


def test_create_registrar_no_parameters():
    response = confd.registrars.post()
    response.assert_match(
        400,
        re.compile(re.escape('main_host')) and re.compile(re.escape('proxy_main_host')),
    )


def test_create_registrar_all_parameters():
    parameters = {
        'deletable': True,
        'name': 'TestRegistrar',
        'main_host': '1.2.3.4',
        'main_port': 5060,
        'backup_host': '1.2.3.5',
        'backup_port': 5061,
        'proxy_main_host': '1.2.3.6',
        'proxy_main_port': 5062,
        'proxy_backup_host': '1.2.3.7',
        'proxy_backup_port': 5063,
        'outbound_proxy_host': '1.2.3.8',
        'outbound_proxy_port': 5064,
    }

    response = confd.registrars.post(**parameters)
    response.assert_created('registrars')
    assert_that(response.item, has_entries(parameters))

    response = confd.registrars(response.item['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.registrar(deletable=False, main_host='1.2.3.4', proxy_main_host='1.2.3.4')
def test_edit_registrar_all_parameters(registrar):
    parameters = {
        'deletable': True,
        'name': 'TestRegistrar',
        'main_host': '1.2.3.4',
        'main_port': 5060,
        'backup_host': '1.2.3.5',
        'backup_port': 5061,
        'proxy_main_host': '1.2.3.6',
        'proxy_main_port': 5062,
        'proxy_backup_host': '1.2.3.7',
        'proxy_backup_port': 5063,
        'outbound_proxy_host': '1.2.3.8',
        'outbound_proxy_port': 5064,
    }

    response = confd.registrars(registrar['id']).put(**parameters)
    response.assert_updated()

    response = confd.registrars(registrar['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.registrar(
    deletable=False,
    name='TestRegistrar',
    main_host='1.2.3.4',
    main_port=5060,
    backup_host='1.2.3.5',
    backup_port=5061,
    proxy_main_host='1.2.3.6',
    proxy_main_port=5062,
    proxy_backup_host='1.2.3.7',
    outbound_proxy_host='1.2.3.8',
    outbound_proxy_port=5063,
)
def test_edit_registrar_null_parameters(registrar):
    response = confd.registrars(registrar['id']).put(
        deletable=True,
        name=None,
        main_host='1.2.3.4',
        main_port=None,
        backup_host=None,
        backup_port=None,
        proxy_main_host='1.2.3.5',
        proxy_main_port=None,
        proxy_backup_host=None,
        proxy_backup_port=None,
        outbound_proxy_host=None,
        outbound_proxy_port=None,
    )
    response.assert_updated()

    response = confd.registrars(registrar['id']).get()
    assert_that(
        response.item,
        has_entries(
            deletable=True,
            name=none(),
            main_host='1.2.3.4',
            main_port=none(),
            backup_host=none(),
            backup_port=none(),
            proxy_main_host='1.2.3.5',
            proxy_main_port=none(),
            proxy_backup_host=none(),
            proxy_backup_port=none(),
            outbound_proxy_host=none(),
            outbound_proxy_port=none(),
        ),
    )


def test_edit_registrar_no_parameters():
    parameters = {
        'deletable': True,
        'name': 'TestRegistrar',
        'main_host': '1.2.3.4',
        'main_port': 5060,
        'backup_host': '1.2.3.5',
        'backup_port': 5061,
        'proxy_main_host': '1.2.3.6',
        'proxy_main_port': 5062,
        'proxy_backup_host': '1.2.3.7',
        'proxy_backup_port': 5063,
        'outbound_proxy_host': '1.2.3.8',
        'outbound_proxy_port': 5064,
    }

    response = confd.registrars.post(**parameters)
    response.assert_created('registrars')

    id_registrar = response.item['id']
    response = confd.registrars(id_registrar).put({})
    response.assert_updated()

    response = confd.registrars(id_registrar).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.registrar(
    main_host='1.2.3.4',
    proxy_main_host='1.2.3.5',
    main_port=5060,
    name='TestRegistrar',
    outbound_proxy_host='1.2.3.6',
    outbound_proxy_port=5061,
)
def test_edit_registrar_updates_autoprov(registrar):
    response = confd.registrars(registrar['id']).put(proxy_main_host='2.3.4.5')
    response.assert_updated()

    autoprov_sip_config = provd.configs.get('autoprov')['raw_config']['sip_lines']['1']
    assert_that(autoprov_sip_config, has_entries(proxy_ip='2.3.4.5'))
    autoprov_sccp_config = provd.configs.get('autoprov')['raw_config'][
        'sccp_call_managers'
    ]['1']
    assert_that(autoprov_sccp_config, has_entries(ip='2.3.4.5'))


@fixtures.registrar(
    id='TestRegistrar',
    main_host='1.2.3.4',
    proxy_main_host='1.2.3.5',
    main_port=5060,
    outbound_proxy_host='1.2.3.6',
    outbound_proxy_port=5061,
)
def test_edit_registrar_updates_sip_device(registrar):
    with line_device(endpoint_type='sip', registrar='TestRegistrar') as (line, device):
        new_registrar_body = {
            'proxy_main_host': '2.3.4.5',
            'proxy_main_port': 4444,
            'main_host': '4.5.6.7',
            'main_port': 5555,
            'outbound_proxy_host': '6.7.8.9',
            'outbound_proxy_port': 6666,
            'proxy_backup_host': '7.8.9.90',
            'proxy_backup_port': 7777,
        }

        response = confd.registrars(registrar['id']).put(**new_registrar_body)
        response.assert_updated()

        config = provd.configs.get(device['id'])['raw_config']['sip_lines']
        assert_that(
            config,
            has_entries(
                {
                    '1': has_entries(
                        proxy_ip=new_registrar_body['proxy_main_host'],
                        proxy_port=new_registrar_body['proxy_main_port'],
                        registrar_port=new_registrar_body['main_port'],
                        registrar_ip=new_registrar_body['main_host'],
                        outbound_proxy_ip=new_registrar_body['outbound_proxy_host'],
                        outbound_proxy_port=new_registrar_body['outbound_proxy_port'],
                        backup_proxy_ip=new_registrar_body['proxy_backup_host'],
                        backup_proxy_port=new_registrar_body['proxy_backup_port'],
                    )
                }
            ),
        )


@fixtures.registrar(
    id='TestRegistrar',
    main_host='1.2.3.4',
    proxy_main_host='1.2.3.5',
    main_port=5060,
    outbound_proxy_host='1.2.3.6',
    outbound_proxy_port=5061,
)
def test_edit_registrar_updates_sccp_device(registrar):
    with line_device(endpoint_type='sccp', registrar='TestRegistrar') as (line, device):
        new_registrar_body = {
            'proxy_main_host': '2.3.4.6',
            'proxy_main_port': 4445,
            'main_host': '4.5.6.8',
            'main_port': 5556,
            'outbound_proxy_host': '6.7.8.99',
            'outbound_proxy_port': 6667,
            'proxy_backup_host': '7.8.9.91',
            'proxy_backup_port': 7778,
        }

        response = confd.registrars(registrar['id']).put(**new_registrar_body)
        response.assert_updated()

        config = provd.configs.get(device['id'])['raw_config']['sccp_call_managers']
        assert_that(
            config,
            has_entries(
                {
                    '1': has_entries(ip=new_registrar_body['proxy_main_host']),
                    '2': has_entries(ip=new_registrar_body['proxy_backup_host']),
                }
            ),
        )


def test_registrar_addresses_without_backup_on_sip_device():
    provd.reset()
    registrar = confd.registrars('default').get().item

    with line_device('sip') as (line, device):
        config = provd.configs.get(device['id'])
        sip_config = config['raw_config']['sip_lines']['1']

        assert_that(
            sip_config,
            has_entries(
                proxy_ip=registrar['proxy_main_host'],
                registrar_ip=registrar['main_host'],
            ),
        )

        assert_that(sip_config, is_not(has_key('backup_proxy_ip')))
        assert_that(sip_config, is_not(has_key('backup_registrar_ip')))


def check_registrar_addresses_without_backup_on_sccp_device():
    provd.reset()
    registrar = confd.registrars('default').get().item

    with line_device('sccp') as (line, device):
        config = provd.configs.get(device['id'])
        sccp_config = config['raw_config']['sccp_call_managers']

        assert_that(
            sccp_config,
            has_entries({'1': has_entries(ip=registrar['proxy_main_host'])}),
        )

        assert_that(sccp_config, is_not(has_key('2')))


@fixtures.registrar()
def test_delete_registrar(registrar):
    response = confd.registrars(registrar['id']).delete()
    response.assert_deleted()


@fixtures.registrar()
def test_restrict_only_master_tenant(registrar):
    response = confd.registrars.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.registrars.post(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.registrars(registrar['id']).get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.registrars(registrar['id']).put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.registrars(registrar['id']).delete(token=TOKEN_SUB_TENANT)
    response.assert_status(401)


@fixtures.registrar()
def test_bus_events(registrar):
    url = confd.registrars(registrar['id'])
    body = {'name': 'a', 'main_host': '1.2.3.4', 'proxy_main_host': '1.2.3.4'}
    headers = {}

    s.check_event('registrar_created', headers, confd.registrars.post, body)
    s.check_event('registrar_edited', headers, url.put)
    s.check_event('registrar_deleted', headers, url.delete)
