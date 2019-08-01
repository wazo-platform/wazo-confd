# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    has_entries,
    has_entry,
    has_item,
    has_items,
    has_length,
    instance_of,
    is_not,
    not_,
)

from . import confd
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

ALL_OPTIONS = [
    ['amaflags', 'default'],
    ['language', 'fr_FR'],
    ['qualify', '500'],
    ['callerid', '"cûstomcallerid" <1234>'],
    ['encryption', 'yes'],
    ['permit', '127.0.0.1'],
    ['deny', '127.0.0.1'],
    ['disallow', 'all'],
    ['allow', 'gsm'],
    ['accountcode', 'accountcode'],
    ['mohinterpret', 'mohinterpret'],
    ['parkinglot', '700'],
    ['fullname', 'fullname'],
    ['defaultip', '127.0.0.1'],
    ['regexten', 'regexten'],
    ['cid_number', '0123456789'],
    ['port', '10000'],
    ['username', 'username'],
    ['secret', 'secret'],
    ['dbsecret', 'dbsecret'],
    ['mailbox', 'mailbox'],
    ['trunk', 'yes'],
    ['auth', 'md5'],
    ['forceencryption', 'aes128'],
    ['maxauthreq', '10'],
    ['inkeys', 'inkeys'],
    ['outkey', 'oukeys'],
    ['adsi', 'yes'],
    ['transfer', 'mediaonly'],
    ['codecpriority', 'disabled'],
    ['jitterbuffer', 'yes'],
    ['forcejitterbuffer', 'yes'],
    ['sendani', 'yes'],
    ['qualifysmoothing', 'yes'],
    ['qualifyfreqok', '100'],
    ['qualifyfreqnotok', '20'],
    ['timezone', 'timezone'],
    ['mohsuggest', 'mohsuggest'],
    ['sourceaddress', 'sourceaddress'],
    ['setvar', 'setvar'],
    ['mask', 'mask'],
    ['peercontext', 'peercontext'],
    ['immediate', 'yes'],
    ['keyrotate', 'yes'],
    ['requirecalltoken', 'yes'],
]


def test_get_errors():
    fake_iax_get = confd.endpoints.iax(999999).get
    s.check_resource_not_found(fake_iax_get, 'IAXEndpoint')


def test_delete_errors():
    with fixtures.iax() as iax:
        fake_iax_delete = confd.endpoints.iax(999999).delete
        s.check_resource_not_found(fake_iax_delete, 'IAXEndpoint')



def test_post_errors():
    url = confd.endpoints.iax.post
    error_checks(url)


def test_put_errors():
    with fixtures.iax() as iax:
        url = confd.endpoints.iax(iax['id']).put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', 123)
    s.check_bogus_field_returns_error(url, 'name', None)
    s.check_bogus_field_returns_error(url, 'name', ']^',)
    s.check_bogus_field_returns_error(url, 'name', 'ûsername')
    s.check_bogus_field_returns_error(url, 'name', [],)
    s.check_bogus_field_returns_error(url, 'name', {},)
    s.check_bogus_field_returns_error(url, 'type', 123)
    s.check_bogus_field_returns_error(url, 'type', 'invalid_choice')
    s.check_bogus_field_returns_error(url, 'type', True)
    s.check_bogus_field_returns_error(url, 'type', None)
    s.check_bogus_field_returns_error(url, 'type', [])
    s.check_bogus_field_returns_error(url, 'type', {})
    s.check_bogus_field_returns_error(url, 'host', 123)
    s.check_bogus_field_returns_error(url, 'host', True)
    s.check_bogus_field_returns_error(url, 'host', None)
    s.check_bogus_field_returns_error(url, 'host', [])
    s.check_bogus_field_returns_error(url, 'host', {})
    s.check_bogus_field_returns_error(url, 'options', 123)
    s.check_bogus_field_returns_error(url, 'options', None)
    s.check_bogus_field_returns_error(url, 'options', {})
    s.check_bogus_field_returns_error(url, 'options', 'string')
    s.check_bogus_field_returns_error(url, 'options', [None])
    s.check_bogus_field_returns_error(url, 'options', ['string', 'string'])
    s.check_bogus_field_returns_error(url, 'options', [123, 123])
    s.check_bogus_field_returns_error(url, 'options', ['string', 123])
    s.check_bogus_field_returns_error(url, 'options', [[]])
    s.check_bogus_field_returns_error(url, 'options', [{'key': 'value'}])
    s.check_bogus_field_returns_error(url, 'options', [['missing_value']])
    s.check_bogus_field_returns_error(url, 'options', [['too', 'much', 'value']])
    s.check_bogus_field_returns_error(url, 'options', [['wrong_value', 1234]])
    s.check_bogus_field_returns_error(url, 'options', [['none_value', None]])

    unique_error_checks(url)


def unique_error_checks(url):
    with fixtures.iax(name='unique') as iax:
        s.check_bogus_field_returns_error(url, 'name', iax['name'])



def test_get():
    with fixtures.iax() as iax:
        response = confd.endpoints.iax(iax['id']).get()
        assert_that(response.item, has_entries({
            'name': has_length(8),
            'type': 'friend',
            'host': 'dynamic',
            'options': instance_of(list),
            'trunk': None,
        }))



def test_get_multi_tenant():
    with fixtures.iax(wazo_tenant=MAIN_TENANT) as main, fixtures.iax(wazo_tenant=SUB_TENANT) as sub:
        response = confd.endpoints.iax(main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='IAXEndpoint'))

        response = confd.endpoints.iax(sub['id']).get(wazo_tenant=MAIN_TENANT)
        assert_that(response.item, has_entries(**sub))



def test_search():
    with fixtures.iax(name='search', type='friend', host='search') as iax, fixtures.iax(name='hidden', type='peer', host='hidden') as hidden:
        url = confd.endpoints.iax
        searches = {
            'name': 'search',
            'type': 'friend',
            'host': 'search'
        }

        for field, term in searches.items():
            check_search(url, iax, hidden, field, term)



def check_search(url, iax, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, iax[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: iax[field]})
    assert_that(response.items, has_item(has_entry('id', iax['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def test_sorting_offset_limit():
    with fixtures.iax(name='sort1') as iax1, fixtures.iax(name='sort2') as iax2:
        url = confd.endpoints.iax.get
        s.check_sorting(url, iax1, iax2, 'name', 'sort')

        s.check_offset(url, iax1, iax2, 'name', 'sort')
        s.check_offset_legacy(url, iax1, iax2, 'name', 'sort')

        s.check_limit(url, iax1, iax2, 'name', 'sort')



def test_list_multi_tenant():
    with fixtures.iax(wazo_tenant=MAIN_TENANT) as main, fixtures.iax(wazo_tenant=SUB_TENANT) as sub:
        response = confd.endpoints.iax.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            all_of(has_items(main)), not_(has_items(sub)),
        )

        response = confd.endpoints.iax.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(has_items(sub), not_(has_items(main))),
        )

        response = confd.endpoints.iax.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(
            response.items,
            has_items(main, sub),
        )



def test_create_minimal_parameters():
    response = confd.endpoints.iax.post()

    response.assert_created('endpoint_iax', location='endpoints/iax')
    assert_that(response.item, has_entries({
        'tenant_uuid': MAIN_TENANT,
        'name': has_length(8),
        'type': 'friend',
        'host': 'dynamic',
        'options': instance_of(list)},
    ))


def test_create_all_parameters():
    response = confd.endpoints.iax.post(
        name="myname",
        type="peer",
        host="127.0.0.1",
        options=ALL_OPTIONS,
    )

    assert_that(response.item, has_entries({
        'tenant_uuid': MAIN_TENANT,
        'name': 'myname',
        'type': 'peer',
        'host': '127.0.0.1',
        'options': has_items(*ALL_OPTIONS)
    }))


def test_create_additional_options():
    options = ALL_OPTIONS + [
        ["foo", "bar"],
        ["spam", "eggs"]
    ]

    response = confd.endpoints.iax.post(options=options)
    assert_that(response.item['options'], has_items(*options))


def test_update_required_parameters():
    with fixtures.iax() as iax:
        response = confd.endpoints.iax(iax['id']).put(
            name="updatedname",
            type="peer",
            host="127.0.0.1"
        )
        response.assert_updated()

        response = confd.endpoints.iax(iax['id']).get()
        assert_that(response.item, has_entries({
            'name': 'updatedname',
            'type': 'peer',
            'host': '127.0.0.1',
        }))



def test_update_options():
    with fixtures.iax(options=[["allow", "gsm"], ["nat", "force_rport,comedia"]]) as iax:
        options = [
            ["allow", "g723"],
            ["insecure", "port"]
        ]

        response = confd.endpoints.iax(iax['id']).put(options=options)
        response.assert_updated()

        response = confd.endpoints.iax(iax['id']).get()
        assert_that(response.item['options'], has_items(*options))



def test_update_additional_options():
    with fixtures.iax(options=[
    ["allow", "gsm"],
    ["foo", "bar"],
    ["foo", "baz"],
    ["spam", "eggs"]
]) as iax:
        options = [
            ["allow", "g723"],
            ["foo", "newbar"],
            ["foo", "newbaz"],
            ["spam", "neweggs"]
        ]

        response = confd.endpoints.iax(iax['id']).put(options=options)
        response.assert_updated()

        response = confd.endpoints.iax(iax['id']).get()
        assert_that(response.item['options'], has_items(*options))



def test_update_values_other_than_host_does_not_touch_it():
    with fixtures.iax(host="static") as iax:
        response = confd.endpoints.iax(iax['id']).put(name="testhost")
        response.assert_ok()

        response = confd.endpoints.iax(iax['id']).get()
        assert_that(response.item, has_entries(host="static"))



def test_edit_multi_tenant():
    with fixtures.iax(wazo_tenant=MAIN_TENANT) as main, fixtures.iax(wazo_tenant=SUB_TENANT) as sub:
        response = confd.endpoints.iax(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='IAXEndpoint'))

        response = confd.endpoints.iax(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()



def test_delete():
    with fixtures.iax() as iax:
        response = confd.endpoints.iax(iax['id']).delete()
        response.assert_deleted()



def test_delete_multi_tenant():
    with fixtures.iax(wazo_tenant=MAIN_TENANT) as main, fixtures.iax(wazo_tenant=SUB_TENANT) as sub:
        response = confd.endpoints.iax(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='IAXEndpoint'))

        response = confd.endpoints.iax(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()

