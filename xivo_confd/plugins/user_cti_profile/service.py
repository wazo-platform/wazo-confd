# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import Session

from xivo_confd.plugins.user_cti_profile import validator, notifier


def edit(user, form):
    cti_profile_id = form.get('cti_profile_id')
    cti_enabled = form.get('cti_enabled')
    if cti_enabled is not None:
        user.cti_enabled = cti_enabled

    with Session.no_autoflush:
        validator.validate_edit(user, cti_profile_id)

    if 'cti_profile_id' in form:
        user.cti_profile_id = cti_profile_id

    notifier.edited(user)
