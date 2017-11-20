# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import Session


class CRUDService(object):

    def __init__(self, dao, validator, notifier, extra_parameters=None):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier
        self.extra_parameters = extra_parameters or []

    def search(self, parameters):
        return self.dao.search(**parameters)

    def get(self, resource_id):
        return self.dao.get(resource_id)

    def find_by(self, **criteria):
        return self.dao.find_by(**criteria)

    def get_by(self, **criteria):
        return self.dao.get_by(**criteria)

    def create(self, resource):
        self.validator.validate_create(resource)
        created_resource = self.dao.create(resource)
        self.notifier.created(created_resource)
        return created_resource

    def edit(self, resource, updated_fields=None):
        with Session.no_autoflush:
            self.validator.validate_edit(resource)
        self.dao.edit(resource)
        self.notifier.edited(resource)

    def delete(self, resource):
        self.validator.validate_delete(resource)
        self.dao.delete(resource)
        self.notifier.deleted(resource)
