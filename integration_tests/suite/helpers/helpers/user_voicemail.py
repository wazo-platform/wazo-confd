# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(user_id, voicemail_id, check=True):
    response = confd.users(user_id).voicemails(voicemail_id).put()
    if check:
        response.assert_ok()


def dissociate(user_id, voicemail_id, check=True):
    response = confd.users(user_id).voicemails.delete()
    if check:
        response.assert_ok()
