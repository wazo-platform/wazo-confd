# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import (
    any_of,
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    has_entries,
    has_items,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT, TOKEN
from . import BaseIntegrationTest, ari, asterisk_sound, confd, wazo_sound

DEFAULT_INTERNAL_DIRECTORY = ('monitor', 'recordings-meetme')
DEFAULT_CATEGORY = ('acd', 'features', 'playback', 'recordings')


def setup_module():
    wazo_sound.create_directory(MAIN_TENANT, name='')
    wazo_sound.create_directory(SUB_TENANT, name='')


def test_get_errors():
    fake_sound = confd.sounds('invalid').get
    s.check_resource_not_found(fake_sound, 'Sound')

    for invalid_name in ['.foo', 'foo/bar', '../bar']:
        response = confd.sounds(invalid_name).get()
        response.assert_status(404)


def test_delete_errors():
    fake_sound = confd.sounds('invalid').delete
    s.check_resource_not_found(fake_sound, 'Sound')


def test_post_errors():
    url = confd.sounds
    error_checks(url.post)
    s.check_missing_body_returns_error(url, 'POST')

    unique_error_checks(url.post)


@fixtures.sound(wazo_tenant=MAIN_TENANT)
def test_search_errors(sound):
    searchable_endpoints = [
        confd.sounds.get,
    ]
    for url in searchable_endpoints:
        s.search_error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', 1234)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(150))
    s.check_bogus_field_returns_error(url, 'name', '.foo')
    s.check_bogus_field_returns_error(url, 'name', 'foo\nbar')
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', {})

    s.check_bogus_field_returns_error(url, 'name', 'system')


@fixtures.sound(name='unique')
def unique_error_checks(url, sound):
    s.check_bogus_field_returns_error(url, 'name', sound['name'])


@fixtures.sound(wazo_tenant=MAIN_TENANT, name='category_1')
@fixtures.sound(wazo_tenant=SUB_TENANT, name='category_2')
def test_list(sound1, sound2):
    sound_system = has_entries(name='system')
    response = confd.sounds.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, has_items(sound1, sound_system))

    response = confd.sounds.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, has_items(sound2, sound_system))

    response = confd.sounds.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(sound1, sound2, sound_system))

    response = confd.sounds.get(wazo_tenant=SUB_TENANT, order='name', limit=1)
    assert_that(response.items, contains(sound2))
    assert_that(response.total, equal_to(2))


@fixtures.sound()
def test_get(main):
    response = confd.sounds(main['name']).get()
    assert_that(response.item, has_entries(name=main['name'], files=empty()))


@fixtures.sound(wazo_tenant=MAIN_TENANT)
@fixtures.sound(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.sounds(main['name']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(name=main['name']))

    response = confd.sounds(main['name']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Sound'))

    response = confd.sounds(sub['name']).get(wazo_tenant=MAIN_TENANT)
    response.assert_match(404, e.not_found(resource='Sound'))


@fixtures.sound(wazo_tenant=MAIN_TENANT)
def test_get_with_files(sound):
    client = _new_sound_file_client()
    client.url.sounds(sound['name']).files('ivr').put(
        wazo_tenant=MAIN_TENANT, query_string={'format': 'slin', 'language': 'fr_FR'}
    ).assert_updated()
    client.url.sounds(sound['name']).files('ivr').put(
        wazo_tenant=MAIN_TENANT, query_string={'format': 'ogg', 'language': 'en_US'}
    ).assert_updated()

    response = confd.sounds(sound['name']).get(wazo_tenant=MAIN_TENANT)
    assert_that(
        response.item,
        has_entries(
            name=sound['name'],
            files=contains_inanyorder(
                has_entries(
                    name='ivr',
                    formats=contains_inanyorder(
                        has_entries(
                            format='slin',
                            language='fr_FR',
                            path=(
                                '/var/lib/wazo/sounds/tenants/{tenant}/{category}/fr_FR/ivr'.format(
                                    tenant=MAIN_TENANT, category=sound['name']
                                )
                            ),
                            text=None,
                        ),
                        has_entries(
                            format='ogg',
                            language='en_US',
                            path=(
                                '/var/lib/wazo/sounds/tenants/{tenant}/{category}/en_US/ivr'.format(
                                    tenant=MAIN_TENANT, category=sound['name']
                                )
                            ),
                            text=None,
                        ),
                    ),
                )
            ),
        ),
    )


@fixtures.sound(name='test_category_1')
@fixtures.sound(name='test_category_2')
def test_search_sound(sound1, sound2):
    s.check_sorting(confd.sounds.get, sound1, sound2, 'name', 'test_category', 'name')


@fixtures.sound(wazo_tenant=MAIN_TENANT, name='test_category_1')
@fixtures.sound(wazo_tenant=SUB_TENANT, name='test_category_2')
def test_search_sound_multi_tenant(sound1, sound2):
    response = confd.sounds.get(wazo_tenant=MAIN_TENANT, search='test_category')
    assert_that(
        response.items,
        contains(
            has_entries(name="test_category_1"),
        ),
    )

    response = confd.sounds.get(
        wazo_tenant=MAIN_TENANT, search='test_category', recurse=True
    )
    assert_that(
        response.items,
        contains_inanyorder(
            has_entries(name='test_category_1'),
            has_entries(name='test_category_2'),
        ),
    )


@fixtures.sound(name='test_offset_1')
@fixtures.sound(name='test_offset_2')
def test_search_sound_offset(sound1, sound2):
    url = confd.sounds.get
    s.check_offset(url, sound1, sound2, 'name', 'test_offset', 'name')


@fixtures.sound(name='test_limit_1')
@fixtures.sound(name='test_limit_2')
def test_search_sound_limit(sound1, sound2):
    url = confd.sounds.get
    s.check_limit(url, sound1, sound2, 'name', 'test_limit', 'name')


def test_get_system_sound():
    sounds = [
        {
            'id': 'conf-now-unmuted',
            'formats': [
                {'language': 'fr_CA', 'format': 'slin'},
                {'language': 'en_US', 'format': 'slin'},
                {'language': 'en_AU', 'format': 'gsm'},
            ],
            'text': 'The conference is now unmuted.',
        }
    ]
    ari.set_sounds(sounds)

    response = confd.sounds('system').get()

    assert_that(
        response.item,
        has_entries(
            name='system',
            files=contains_inanyorder(
                has_entries(
                    name=sounds[0]['id'],
                    formats=contains_inanyorder(
                        has_entries(
                            format=sounds[0]['formats'][0]['format'],
                            language=sounds[0]['formats'][0]['language'],
                            text=None,
                        ),
                        has_entries(
                            format=sounds[0]['formats'][1]['format'],
                            language=sounds[0]['formats'][1]['language'],
                            text=sounds[0]['text'],
                        ),
                        has_entries(
                            format=sounds[0]['formats'][2]['format'],
                            language=sounds[0]['formats'][2]['language'],
                            text=None,
                        ),
                    ),
                )
            ),
        ),
    )
    ari.reset()


def test_get_system_sound_remove_non_standard_language():
    sounds = [
        {
            'id': 'conf-now-unmuted',
            'formats': [
                {'language': 'recordings', 'format': 'slin'},
                {'language': 'en', 'format': 'slin'},
            ],
            'text': 'text',
        }
    ]
    ari.set_sounds(sounds)

    response = confd.sounds('system').get()

    assert_that(response.item, has_entries(name='system', files=empty()))
    ari.reset()


def test_get_internal_directory():
    for name in DEFAULT_INTERNAL_DIRECTORY:
        response = confd.sounds(name).get()
        response.assert_status(404)


def test_create_minimal_parameters():
    response = confd.sounds.post(wazo_tenant=MAIN_TENANT, name='sound1')
    response.assert_created('sound')

    assert_that(
        response.item,
        has_entries({'tenant_uuid': MAIN_TENANT, 'name': 'sound1', 'files': empty()}),
    )

    confd.sounds(response.item['name']).delete(wazo_tenant=MAIN_TENANT).assert_deleted()


def test_create_all_parameters():
    test_create_minimal_parameters()


def test_create_unauthorized_tenant():
    response = confd.sounds.post(wazo_tenant='wrong_tenant', name='sound1')
    response.assert_status(401)


@fixtures.sound()
def test_edit_unimplemented(sound):
    response = confd.sounds(sound['name']).put()
    response.assert_status(405)


@fixtures.sound()
def test_delete(sound):
    response = confd.sounds(sound['name']).delete()
    response.assert_deleted()
    response = confd.sounds(sound['name']).get()
    response.assert_match(404, e.not_found(resource='Sound'))


@fixtures.sound(wazo_tenant=MAIN_TENANT)
@fixtures.sound(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.sounds(main['name']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Sound'))

    response = confd.sounds(main['name']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_status(204)

    response = confd.sounds(sub['name']).get(wazo_tenant=MAIN_TENANT)
    response.assert_match(404, e.not_found(resource='Sound'))


def test_delete_system_sound():
    response = confd.sounds('system').delete()
    response.assert_status(400)


def test_delete_default_sound():
    for name in DEFAULT_CATEGORY:
        wazo_sound.create_directory(MAIN_TENANT, name)
        response = confd.sounds(name).delete(wazo_tenant=MAIN_TENANT)
        response.assert_status(400)


def test_delete_internal_directory():
    for name in DEFAULT_INTERNAL_DIRECTORY:
        wazo_sound.create_directory(MAIN_TENANT, name)
        response = confd.sounds(name).delete(wazo_tenant=MAIN_TENANT)
        response.assert_status(404)


@fixtures.sound()
def test_get_file_errors(sound):
    response = confd.sounds(sound['name']).files('ivr').get()
    response.assert_status(404)

    client = _new_sound_file_client()
    client.url.sounds(sound['name']).files('ivr').put(
        query_string={'format': 'slin', 'language': 'fr_FR'}
    ).assert_updated()

    response = (
        confd.sounds(sound['name']).files('ivr').get(format='slin', language='invalid')
    )
    response.assert_status(404)

    response = (
        confd.sounds(sound['name']).files('ivr').get(format='ogg', language='fr_FR')
    )
    response.assert_status(404)


@fixtures.sound()
def test_put_file_errors(sound):
    client = _new_sound_file_client()
    filenames = ['.foo', 'foo/bar', '../bar']
    for filename in filenames:
        response = client.url.sounds(sound['name']).files(filename).put()
        response.assert_status(404)

    for invalid_name in ['.foo', 'foo/bar', '../bar']:
        response = client.url.sounds(invalid_name).files('foo').put()
        response.assert_status(404)

    response = client.url.sounds('invalid').files('foo').put()
    response.assert_status(404)


@fixtures.sound()
def test_get_file(sound):
    client = _new_sound_file_client()
    client.url.sounds(sound['name']).files('ivr').put(
        content='ivr_slin_fr_FR', query_string={'format': 'slin', 'language': 'fr_FR'}
    ).assert_updated()
    client.url.sounds(sound['name']).files('ivr').put(
        content='ivr_ogg_fr_FR', query_string={'format': 'ogg', 'language': 'fr_FR'}
    ).assert_updated()
    client.url.sounds(sound['name']).files('ivr').put(
        content='ivr_ogg_fr_CA', query_string={'format': 'ogg', 'language': 'fr_CA'}
    ).assert_updated()

    response = confd.sounds(sound['name']).files('ivr').get(format='ogg')
    assert_that(response.raw, any_of('ivr_ogg_fr_FR', 'ivr_ogg_fr_CA'))
    response.assert_content_disposition('ivr.ogg')

    response = (
        confd.sounds(sound['name']).files('ivr').get(format='ogg', language='fr_FR')
    )
    assert_that(response.raw, equal_to('ivr_ogg_fr_FR'))
    response.assert_content_disposition('ivr.ogg')

    response = confd.sounds(sound['name']).files('ivr').get(language='fr_FR')
    assert_that(response.raw, any_of('ivr_ogg_fr_FR', 'ivr_slin_fr_FR'))

    response = (
        confd.sounds(sound['name'])
        .files('ivr')
        .get(wazo_tenant=MAIN_TENANT, format='slin', language='fr_FR')
    )
    assert_that(response.raw, equal_to('ivr_slin_fr_FR'))
    response.assert_content_disposition('ivr.wav')


def test_get_file_system_errors():
    asterisk_sound.create_directory(MAIN_TENANT, 'recordings')
    asterisk_sound.create_file(MAIN_TENANT, 'recordings/invalid-language.mp3')
    sound = {
        'id': 'invalid-language',
        'formats': [{'language': 'recordings', 'format': 'mp3'}],
        'text': 'asterisk sound test',
    }
    ari.set_sound(sound)

    response = confd.sounds('system').files(sound['id']).get(wazo_tenant=MAIN_TENANT)
    response.assert_status(404)
    ari.reset()


def test_get_file_system():
    asterisk_sound.create_directory('fr_FR')
    asterisk_sound.create_directory('fr_CA')
    asterisk_sound.create_file(
        'fr_FR/asterisk-sound.ogg', content='asterisk_sound_ogg_fr_FR'
    )
    asterisk_sound.create_file(
        'fr_FR/asterisk-sound.wav', content='asterisk_sound_slin_fr_FR'
    )
    asterisk_sound.create_file(
        'fr_CA/asterisk-sound.ogg', content='asterisk_sound_ogg_fr_CA'
    )
    sound = {
        'id': 'asterisk-sound',
        'formats': [
            {'language': 'fr_FR', 'format': 'slin'},
            {'language': 'fr_FR', 'format': 'ogg'},
            {'language': 'fr_CA', 'format': 'ogg'},
        ],
        'text': 'Asterisk Sound test',
    }
    ari.set_sound(sound)

    response = confd.sounds('system').files(sound['id']).get(format='ogg')
    assert_that(
        response.raw, any_of('asterisk_sound_ogg_fr_FR', 'asterisk_sound_ogg_fr_CA')
    )
    response.assert_content_disposition('asterisk-sound.ogg')

    response = (
        confd.sounds('system').files(sound['id']).get(format='ogg', language='fr_FR')
    )
    assert_that(response.raw, any_of('asterisk_sound_ogg_fr_FR'))
    response.assert_content_disposition('asterisk-sound.ogg')

    response = confd.sounds('system').files(sound['id']).get(language='fr_FR')
    assert_that(
        response.raw, any_of('asterisk_sound_ogg_fr_FR', 'asterisk_sound_slin_fr_FR')
    )

    response = (
        confd.sounds('system').files(sound['id']).get(format='slin', language='fr_FR')
    )
    assert_that(response.raw, any_of('asterisk_sound_slin_fr_FR'))
    response.assert_content_disposition('asterisk-sound.wav')

    ari.reset()


@fixtures.sound()
def test_get_file_return_without_format_and_language_first(sound):
    client = _new_sound_file_client()
    client.url.sounds(sound['name']).files('ivr').put(
        content='ivr_ogg_fr_FR', query_string={'format': 'ogg', 'language': 'fr_FR'}
    ).assert_updated()
    client.url.sounds(sound['name']).files('ivr').put(
        content='ivr_fr_FR', query_string={'language': 'fr_FR'}
    ).assert_updated()
    client.url.sounds(sound['name']).files('ivr').put(
        content='ivr_ogg', query_string={'format': 'ogg'}
    ).assert_updated()
    client.url.sounds(sound['name']).files('ivr').put(content='ivr').assert_updated()

    response = confd.sounds(sound['name']).files('ivr').get()
    assert_that(response.raw, equal_to('ivr'))
    response.assert_content_disposition('ivr')

    response = confd.sounds(sound['name']).files('ivr').get(format='ogg')
    assert_that(response.raw, equal_to('ivr_ogg'))
    response.assert_content_disposition('ivr.ogg')

    response = confd.sounds(sound['name']).files('ivr').get(language='fr_FR')
    assert_that(response.raw, equal_to('ivr_fr_FR'))
    response.assert_content_disposition('ivr')


@fixtures.sound()
def test_add_update_delete_file(sound):
    client = _new_sound_file_client()

    # add a new file
    response = (
        client.url.sounds(sound['name'])
        .files('foo')
        .put(content='content is not checked')
    )
    response.assert_status(204)

    response = client.url.sounds(sound['name']).files('foo').get()
    assert_that(response.raw, equal_to('content is not checked'))

    response = confd.sounds(sound['name']).get()
    assert_that(response.item, has_entries(files=contains(has_entries(name='foo'))))

    # update/overwrite the file
    response = (
        client.url.sounds(sound['name']).files('foo').put(content='some new content')
    )
    response.assert_status(204)

    response = client.url.sounds(sound['name']).files('foo').get()
    assert_that(response.raw, equal_to('some new content'))

    # delete the file
    response = client.url.sounds(sound['name']).files('foo').delete()
    response.assert_deleted()

    response = confd.sounds(sound['name']).get()
    assert_that(response.item, has_entries(files=empty()))


@fixtures.sound(wazo_tenant=MAIN_TENANT)
@fixtures.sound(wazo_tenant=SUB_TENANT)
def test_add_update_delete_file_multi_tenant(main, sub):
    client = _new_sound_file_client()

    # add a new files
    response = (
        client.url.sounds(main['name'])
        .files('foo')
        .put(wazo_tenant=SUB_TENANT, content='content is not checked')
    )
    response.assert_match(404, e.not_found(resource='Sound'))
    response = (
        client.url.sounds(sub['name'])
        .files('foo')
        .put(wazo_tenant=MAIN_TENANT, content='content is not checked')
    )
    response.assert_match(404, e.not_found(resource='Sound'))
    response = (
        client.url.sounds(main['name'])
        .files('foo')
        .put(wazo_tenant=MAIN_TENANT, content='content is not checked')
    )
    response.assert_status(204)
    response = (
        client.url.sounds(sub['name'])
        .files('foo')
        .put(wazo_tenant=SUB_TENANT, content='content is not checked')
    )
    response.assert_status(204)

    # get the files
    response = client.url.sounds(main['name']).files('foo').get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Sound'))

    response = client.url.sounds(sub['name']).files('foo').get(wazo_tenant=MAIN_TENANT)
    response.assert_match(404, e.not_found(resource='Sound'))

    # update the files
    response = (
        client.url.sounds(main['name'])
        .files('foo')
        .put(wazo_tenant=SUB_TENANT, content='some new content')
    )
    response.assert_match(404, e.not_found(resource='Sound'))
    response = (
        client.url.sounds(sub['name'])
        .files('foo')
        .put(wazo_tenant=MAIN_TENANT, content='some new content')
    )
    response.assert_match(404, e.not_found(resource='Sound'))

    # delete the files
    response = (
        client.url.sounds(main['name']).files('foo').delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found(resource='Sound'))

    response = (
        client.url.sounds(sub['name']).files('foo').delete(wazo_tenant=MAIN_TENANT)
    )
    response.assert_match(404, e.not_found(resource='Sound'))


@fixtures.sound()
def test_delete_file_multiple(sound):
    client = _new_sound_file_client()
    client.url.sounds(sound['name']).files('ivr').put(
        query_string={'format': 'slin', 'language': 'fr_FR'}
    ).assert_updated()
    client.url.sounds(sound['name']).files('ivr').put(
        query_string={'format': 'ogg'}
    ).assert_updated()
    client.url.sounds(sound['name']).files('ivr').put(
        query_string={'format': 'slin', 'language': 'fr_CA'}
    ).assert_updated()

    confd.sounds(sound['name']).files('ivr').delete().assert_deleted()

    response = confd.sounds(sound['name']).files('ivr').get()
    response.assert_status(404)


@fixtures.sound(wazo_tenant=MAIN_TENANT)
def test_delete_files_with_partial_errors(sound):
    wazo_sound.create_directory(
        MAIN_TENANT, '{}/fr_FR'.format(sound['name']), mode='555'
    )
    wazo_sound.create_file(
        MAIN_TENANT, '{}/fr_FR/ivr.mp3'.format(sound['name']), mode='444'
    )
    client = _new_sound_file_client()
    client.url.sounds(sound['name']).files('ivr').put(
        wazo_tenant=MAIN_TENANT
    ).assert_updated()

    response = confd.sounds(sound['name']).files('ivr').delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()

    response = confd.sounds(sound['name']).files('ivr').delete(wazo_tenant=MAIN_TENANT)
    response.assert_status(500)


def test_get_system_file_errors():
    response = confd.sounds('system').files('invalid').get()
    response.assert_status(404)


def test_update_system_file():
    sound = {'id': 'foo', 'formats': []}
    ari.set_sound(sound)
    client = _new_sound_file_client()
    response = client.url.sounds('system').files('foo').put()
    response.assert_status(400)


def test_delete_system_file():
    sound = {'id': 'foo', 'formats': []}
    ari.set_sound(sound)
    response = confd.sounds('system').files('foo').delete()
    response.assert_status(400)


# XXX set this client in BaseIntegrationTest
def _new_sound_file_client():
    def encoder(data):
        default_content = 'I do not care of content'
        if data is None:
            return default_content
        return data.get('content', default_content)

    return BaseIntegrationTest.new_client(
        headers={"Content-Type": "application/octet-stream", "X-Auth-Token": TOKEN},
        encoder=encoder,
    )


def test_bus_events():
    headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event('sound_created', headers, confd.sounds.post, {'name': 'bus_event'})
    s.check_event('sound_deleted', headers, confd.sounds('bus_event').delete)
