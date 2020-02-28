# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries, starts_with
from . import confd


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
