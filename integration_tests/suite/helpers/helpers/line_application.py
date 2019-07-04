# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(line_id, application_uuid, check=True):
    response = confd.lines(line_id).applications(application_uuid).put()
    if check:
        response.assert_ok()


def dissociate(line_id, application_uuid, check=True):
    response = confd.lines(line_id).applications(application_uuid).delete()
    if check:
        response.assert_ok()
