# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def add(guest_uuid, meeting_uuid, **params):
    response = (
        confd.guests(guest_uuid).meetings(meeting_uuid).authorizations.post(params)
    )
    return response.item


def delete(guest_uuid, meeting_uuid, uuid, check=False, **params):
    response = (
        confd.guests(guest_uuid).meetings(meeting_uuid).authorizations(uuid).delete()
    )
    if check:
        response.assert_ok()


def generate(guest_uuid, meeting, **params):
    params.setdefault('guest_name', 'Meeting Guest')
    return add(guest_uuid, meeting['uuid'], **params)
