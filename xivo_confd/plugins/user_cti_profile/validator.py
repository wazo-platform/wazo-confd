# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.cti_profile import dao as cti_profile_dao


def validate_edit(user, cti_profile_id):
    if cti_profile_id is not None:
        _validate_cti_profile_exists(cti_profile_id)
    _validate_user_has_login_passwd(user)


def _validate_cti_profile_exists(cti_profile_id):
    try:
        cti_profile_dao.get(cti_profile_id)
    except NotFoundError:
        raise errors.param_not_found('cti_profile_id', 'CtiProfile')


def _validate_user_has_login_passwd(user):
    if user.cti_enabled:
        if not user.username or not user.password:
            raise errors.missing_cti_parameters(user_id=user.id)
