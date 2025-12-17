# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import io
import wave

from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    empty,
    equal_to,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT, TOKEN
from . import BaseIntegrationTest, confd

NOT_FOUND_UUID = 'uuid-not-found'
VALID_WAV_FILE = io.BytesIO()
VALID_WAV_FILE_2 = io.BytesIO()
INVALID_WAV_FILE_CHANNELS = io.BytesIO()
INVALID_WAV_FILE_SAMPLE = io.BytesIO()
INVALID_WAV_FILE_FRAMERATE = io.BytesIO()

with wave.open(VALID_WAV_FILE, 'wb') as wav_file:
    wav_file.setnchannels(1)  # mono
    wav_file.setsampwidth(2)  # 16 bits
    wav_file.setframerate(8000)  # 8 kHz
    wav_file.writeframes(b'random content')


with wave.open(VALID_WAV_FILE_2, 'wb') as wav_file:
    wav_file.setnchannels(1)  # mono
    wav_file.setsampwidth(2)  # 16 bits
    wav_file.setframerate(16000)  # 16 kHz
    wav_file.writeframes(b'random content 2')


with wave.open(INVALID_WAV_FILE_CHANNELS, 'wb') as wav_file:
    wav_file.setnchannels(2)  # stereo (2) channels
    wav_file.setsampwidth(2)  # 16 bits
    wav_file.setframerate(8000)  # 8 kHz
    wav_file.writeframes(b'random content 3')


with wave.open(INVALID_WAV_FILE_SAMPLE, 'wb') as wav_file:
    wav_file.setnchannels(1)  # mono
    wav_file.setsampwidth(4)  # 32 bits (4 bytes)
    wav_file.setframerate(8000)  # 8 kHz
    wav_file.writeframes(b'random content 4')


with wave.open(INVALID_WAV_FILE_FRAMERATE, 'wb') as wav_file:
    wav_file.setnchannels(1)  # mono
    wav_file.setsampwidth(2)  # 16 bits
    wav_file.setframerate(44100)  # 44.1kHz frame (sample) rate
    wav_file.writeframes(b'random content 5')


def test_get_errors():
    fake_moh = confd.moh(NOT_FOUND_UUID).get
    s.check_resource_not_found(fake_moh, 'MOH')


def test_delete_errors():
    fake_moh = confd.moh(NOT_FOUND_UUID).delete
    s.check_resource_not_found(fake_moh, 'MOH')


def test_post_errors():
    url = confd.moh
    error_checks(url.post)
    s.check_missing_body_returns_error(url, 'POST')

    s.check_bogus_field_returns_error(
        url.post, 'name', s.random_string(129), None, 'label'
    )


@fixtures.moh()
def test_put_errors(moh):
    url = confd.moh(moh['uuid'])
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'label', True)
    s.check_bogus_field_returns_error(url, 'label', 1234)
    s.check_bogus_field_returns_error(url, 'label', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'label', [])
    s.check_bogus_field_returns_error(url, 'label', {})
    s.check_bogus_field_returns_error(url, 'mode', True)
    s.check_bogus_field_returns_error(url, 'mode', 1234)
    s.check_bogus_field_returns_error(url, 'mode', 'hello')
    s.check_bogus_field_returns_error(url, 'mode', [])
    s.check_bogus_field_returns_error(url, 'mode', {})
    s.check_bogus_field_returns_error(url, 'application', True)
    s.check_bogus_field_returns_error(url, 'application', 1234)
    s.check_bogus_field_returns_error(url, 'application', s.random_string(257))
    s.check_bogus_field_returns_error(url, 'application', [])
    s.check_bogus_field_returns_error(url, 'application', {})
    s.check_bogus_field_returns_error(url, 'sort', True)
    s.check_bogus_field_returns_error(url, 'sort', 1234)
    s.check_bogus_field_returns_error(url, 'sort', 'hello')
    s.check_bogus_field_returns_error(url, 'sort', [])
    s.check_bogus_field_returns_error(url, 'sort', {})


@fixtures.moh(label='visible')
@fixtures.moh(label='hidden')
def test_search(visible, hidden):
    url = confd.moh
    searches = {'label': 'visible'}

    for field, term in searches.items():
        check_search(url, visible, hidden, field, term)


def check_search(url, visible, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, visible[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: visible[field]})
    assert_that(response.items, has_item(has_entry('uuid', visible['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))


@fixtures.moh(label='sort1')
@fixtures.moh(label='sort2')
def test_sorting_offset_limit(moh1, moh2):
    url = confd.moh.get
    s.check_sorting(url, moh1, moh2, 'label', 'sort', 'uuid')

    s.check_offset(url, moh1, moh2, 'label', 'sort', 'uuid')
    s.check_limit(url, moh1, moh2, 'label', 'sort', 'uuid')


@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.moh.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.moh.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.moh.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.moh()
def test_get(moh):
    response = confd.moh(moh['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            uuid=moh['uuid'],
            name=moh['name'],
            label=moh['label'],
            mode=moh['mode'],
            application=moh['application'],
            sort=moh['sort'],
            files=empty(),
        ),
    )


@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.moh(main['uuid']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='MOH'))

    response = confd.moh(sub['uuid']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.moh.post(label='moh1', mode='files')
    response.assert_created('moh')

    assert_that(
        response.item, has_entries(uuid=is_not(empty()), tenant_uuid=MAIN_TENANT)
    )

    confd.moh(response.item['uuid']).delete().assert_deleted()


def test_create_all_parameters():
    response = confd.moh.post(
        label='MOH 1',
        mode='custom',
        application='/usr/bin/mpg123 xxx',
        sort='alphabetical',
    )
    response.assert_created('moh')

    assert_that(
        response.item,
        has_entries(
            tenant_uuid=MAIN_TENANT,
            name=not_(empty()),
            label='MOH 1',
            mode='custom',
            application='/usr/bin/mpg123 xxx',
            sort='alphabetical',
            files=empty(),
        ),
    )

    confd.moh(response.item['uuid']).delete().assert_deleted()


def test_create_deprecated_name():
    response = confd.moh.post(name='MyMOH', mode='files')
    response.assert_created('moh')

    assert_that(
        response.item,
        has_entries(
            uuid=not_(empty()),
            name=not_(empty()),
            label='MyMOH',
        ),
    )

    confd.moh(response.item['uuid']).delete().assert_deleted()


def test_create_custom_mode_with_application():
    response = confd.moh.post(label='moh', mode='custom', application='/bin/false')
    response.assert_created('moh')
    confd.moh(response.item['uuid']).delete().assert_deleted()


def test_create_custom_mode_without_application():
    response = confd.moh.post(label='moh', mode='custom')
    response.assert_status(400)


def test_create_valid_sort():
    valid_sorts = ['alphabetical', 'random', 'random_start']
    for sort in valid_sorts:
        response = confd.moh.post(label='moh', mode='files', sort=sort)
        response.assert_created('moh')
        confd.moh(response.item['uuid']).delete().assert_deleted()


@fixtures.moh()
def test_edit_minimal_parameters(moh):
    response = confd.moh(moh['uuid']).put()
    response.assert_updated()


@fixtures.moh()
def test_edit_all_parameters(moh):
    parameters = {'label': 'Foo', 'application': '/bin/rm -rf /', 'sort': 'random'}

    response = confd.moh(moh['uuid']).put(**parameters)
    response.assert_updated()

    response = confd.moh(moh['uuid']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.moh(mode='files', application=None)
def test_edit_custom_mode_with_application(moh):
    response = confd.moh(moh['uuid']).put(mode='custom', application='/bin/false')
    response.assert_updated()


@fixtures.moh(mode='files', application=None)
def test_edit_custom_mode_without_application(moh):
    response = confd.moh(moh['uuid']).put(mode='custom')
    response.assert_status(400)


@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.moh(main['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='MOH'))

    response = confd.moh(sub['uuid']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.moh()
def test_delete(moh):
    response = confd.moh(moh['uuid']).delete()
    response.assert_deleted()
    response = confd.moh(moh['uuid']).get()
    response.assert_match(404, e.not_found(resource='MOH'))


@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.moh(main['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='MOH'))

    response = confd.moh(sub['uuid']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.moh()
def test_add_update_delete_filename(moh):
    client = _new_moh_file_client()

    # add a new file
    response = (
        client.url.moh(moh['uuid'])
        .files('foo.wav')
        .put(content=VALID_WAV_FILE.getvalue())
    )
    response.assert_status(204)

    response = client.url.moh(moh['uuid']).files('foo.wav').get()
    assert_that(response.content, equal_to(VALID_WAV_FILE.getvalue()))
    response.assert_content_disposition('foo.wav')

    response = confd.moh(moh['uuid']).get()
    assert_that(response.item, has_entries(files=contains_exactly({'name': 'foo.wav'})))

    # update/overwrite the file
    response = (
        client.url.moh(moh['uuid'])
        .files('foo.wav')
        .put(content=VALID_WAV_FILE_2.getvalue())
    )
    response.assert_status(204)

    response = client.url.moh(moh['uuid']).files('foo.wav').get()
    assert_that(response.content, equal_to(VALID_WAV_FILE_2.getvalue()))

    # delete the file
    response = client.url.moh(moh['uuid']).files('foo.wav').delete()
    response.assert_deleted()

    response = confd.moh(moh['uuid']).get()
    assert_that(response.item, has_entries(files=empty()))

    # Test invalid WAV files
    response = (
        client.url.moh(moh['uuid'])
        .files('foo.wav')
        .put(content=INVALID_WAV_FILE_CHANNELS.getvalue())
    )
    response.assert_status(400)

    response = (
        client.url.moh(moh['uuid'])
        .files('foo.wav')
        .put(content=INVALID_WAV_FILE_SAMPLE.getvalue())
    )
    response.assert_status(400)


@fixtures.moh(mode='mp3')
def test_add_file_when_mp3(moh):
    client = _new_moh_file_client()

    # An invalid WAV file uploaded in MP3 mode should not raise an error
    response = (
        client.url.moh(moh['uuid'])
        .files('foo.wav')
        .put(content=INVALID_WAV_FILE_SAMPLE.getvalue())
    )
    response.assert_status(204)


@fixtures.moh(tenant_uuid=MAIN_TENANT)
def test_add_update_delete_filename_multi_tenant(moh):
    client = _new_moh_file_client()

    response = (
        client.url.moh(moh['uuid'])
        .files('foo.wav')
        .put(content=VALID_WAV_FILE.getvalue(), wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found(resource='MOH'))

    response = client.url.moh(moh['uuid']).files('foo.wav').get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='MOH'))

    response = (
        client.url.moh(moh['uuid']).files('foo.wav').delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found(resource='MOH'))

    # valid tenant
    response = (
        client.url.moh(moh['uuid'])
        .files('foo.wav')
        .put(content=VALID_WAV_FILE.getvalue(), wazo_tenant=MAIN_TENANT)
    )
    response.assert_status(204)

    response = client.url.moh(moh['uuid']).files('foo.wav').get(wazo_tenant=MAIN_TENANT)
    assert_that(response.content, equal_to(VALID_WAV_FILE.getvalue()))

    response = (
        client.url.moh(moh['uuid']).files('foo.wav').delete(wazo_tenant=MAIN_TENANT)
    )
    response.assert_deleted()


@fixtures.moh()
def test_add_filename_errors(moh):
    client = _new_moh_file_client()
    filenames = ['.foo.wav', 'foo/bar.wav', '../bar.wav']
    for filename in filenames:
        response = (
            client.url.moh(moh['uuid'])
            .files(filename)
            .put(content=VALID_WAV_FILE.getvalue())
        )
        assert_that(
            response.status,
            equal_to(404),
            'unexpected status for MOH filename {}'.format(filename),
        )


def _new_moh_file_client():
    def encoder(data):
        if data is None:
            return None
        return data['content']

    return BaseIntegrationTest.new_client(
        headers={"Content-Type": "application/octet-stream", "X-Auth-Token": TOKEN},
        encoder=encoder,
    )


@fixtures.moh()
def test_bus_events(moh):
    url = confd.moh(moh['uuid'])
    headers = {'tenant_uuid': moh['tenant_uuid']}

    s.check_event(
        'moh_created',
        headers,
        confd.moh.post,
        {
            'name': 'bus_event',
            'mode': 'files',
        },
    )
    s.check_event('moh_edited', headers, url.put)
    s.check_event('moh_deleted', headers, url.delete)
