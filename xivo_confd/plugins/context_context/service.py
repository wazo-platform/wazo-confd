# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .notifier import build_notifier
from .validator import build_validator


class ContextContextService:

    def __init__(self, context_dao, notifier, validator):
        self.context_dao = context_dao
        self.notifier = notifier
        self.validator = validator

    def associate_contexts(self, context, contexts):
        self.validator.validate_association(context, contexts)
        self.context_dao.associate_contexts(context, contexts)
        self.notifier.associated_contexts(context, contexts)


def build_service(context_dao):
    return ContextContextService(context_dao,
                                 build_notifier(),
                                 build_validator())
