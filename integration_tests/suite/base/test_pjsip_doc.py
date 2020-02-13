# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from requests.exceptions import ConnectionError
from hamcrest import assert_that, has_entries, starts_with
from xivo_test_helpers import until

from . import BaseIntegrationTest, confd, asterisk_json_doc


def test_get():
    response = confd.asterisk.pjsip.doc.get()
    response.assert_ok()
    assert_that(
        response.json,
        has_entries(
            aor=has_entries(),
            auth=has_entries(),
            contact=has_entries(),
            endpoint=has_entries(
                direct_media_method=has_entries(
                    name='direct_media_method',
                    default='invite',
                    synopsis='Direct Media method type',
                    description=starts_with('Method for setting up'),
                    choices=has_entries(
                        invite='', reinvite='Alias for the "invite" value.', update='',
                    ),
                )
            ),
            system=has_entries(),
            transport=has_entries(),
        ),
    )


def test_get_file_error():
    config_filename = 'pjsip.json.gz'
    temp_filename = 'foo.json.gz'

    # restart confd to avoid the cached value
    BaseIntegrationTest.restart_service(service_name='confd')
    asterisk_json_doc.move_file(config_filename, temp_filename)
    confd.obj = None  # reset the singletonproxy to a new instance on the new port

    def check():
        try:
            response = confd.asterisk.pjsip.doc.get()
            response.assert_status(400)
        except ConnectionError:
            assert False, 'Received a ConnectionError'

    try:
        until.assert_(check, timeout=5)
    finally:
        asterisk_json_doc.move_file(temp_filename, config_filename)
