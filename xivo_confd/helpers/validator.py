# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import abc

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError


class Validator(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate(self, model):
        return


class MissingFields(Validator):

    def validate(self, model):
        missing = model.missing_parameters()
        if missing:
            raise errors.missing(*missing)


class RequiredFields(Validator):

    def __init__(self, *fields):
        self.fields = fields

    def validate(self, model):
        required = [field for field in self.fields
                    if getattr(model, field) is None]
        if required:
            raise errors.missing(*required)


class GetResource(Validator):

    def __init__(self, field, dao_get, resource='Resource'):
        self.field = field
        self.dao_get = dao_get
        self.resource = resource

    def validate(self, model):
        value = getattr(model, self.field)
        try:
            self.dao_get(value)
        except NotFoundError:
            metadata = {self.field: value}
            raise errors.param_not_found(self.field, self.resource, **metadata)


class UniqueField(Validator):

    def __init__(self, field, dao_find, resource='Resource'):
        self.field = field
        self.dao_find = dao_find
        self.resource = resource

    def validate(self, model):
        value = getattr(model, self.field)
        found = self.dao_find(value)
        if found is not None:
            metadata = {self.field: value}
            raise errors.resource_exists(self.resource, **metadata)


class FindResource(Validator):

    def __init__(self, field, dao_find, resource='Resource'):
        self.field = field
        self.dao_find = dao_find
        self.resource = resource

    def validate(self, model):
        value = getattr(model, self.field)
        found = self.dao_find(value)
        if found is None:
            metadata = {self.field: value}
            raise errors.param_not_found(self.field, self.resource, **metadata)


class ResourceExists(Validator):

    def __init__(self, field, dao_exist, resource='Resource'):
        self.field = field
        self.dao_exist = dao_exist
        self.resource = resource

    def validate(self, model):
        value = getattr(model, self.field)
        exists = self.dao_exist(value)
        if not exists:
            metadata = {self.field: value}
            raise errors.param_not_found(self.field, self.resource, **metadata)


class Optional(Validator):

    def __init__(self, field, validator):
        self.field = field
        self.validator = validator

    def validate(self, model):
        value = getattr(model, self.field)
        if value is not None:
            self.validator.validate(model)


class MemberOfSequence(Validator):

    def __init__(self, field, dao_list, resource='Resource'):
        self.field = field
        self.resource = resource
        self.dao_list = dao_list

    def validate(self, model):
        value = getattr(model, self.field)
        items = self.dao_list()
        if value not in items:
            metadata = {self.field: value}
            raise errors.param_not_found(self.field, self.resource, **metadata)


class ValidationGroup(object):

    def __init__(self, common=None, create=None, edit=None, delete=None):
        self.common = common or []
        self.create = create or []
        self.edit = edit or []
        self.delete = delete or []

    def validate_create(self, model):
        for validator in self.common + self.create:
            validator.validate(model)

    def validate_edit(self, model):
        for validator in self.common + self.edit:
            validator.validate(model)

    def validate_delete(self, model):
        for validator in self.common + self.delete:
            validator.validate(model)


class AssociationValidator(object):

    def __init__(self, common=None, association=None, dissociation=None):
        self.common = common or []
        self.association = association or []
        self.dissociation = dissociation or []

    def validate_association(self, *models):
        for validator in self.common + self.association:
            validator.validate(*models)

    def validate_dissociation(self, *models):
        for validator in self.common + self.dissociation:
            validator.validate(*models)
