# -*- coding: UTF-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import abc

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

EXTEN_REGEX = r'^_[*#0-9_XxZzNn\[\].!-]{1,39}$|[*#0-9]{1,40}$'
EXTEN_OUTCALL_REGEX = r'^_?\+?[*#0-9_XxZzNn\[\].!-]*$'
LANGUAGE_REGEX = r"^[a-z]{2}_[A-Z]{2}$"


class Validator(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate(self, model):
        return


class ValidatorAssociation(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate(self, model1, model2):
        return


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


class UniqueFieldChanged(Validator):

    def __init__(self, field, dao, resource='Resource'):
        self.field = field
        self.dao = dao
        self.resource = resource

    def validate(self, model):
        value = getattr(model, self.field)
        query = {self.field: value}
        found = self.dao.find_by(**query)
        if found is not None and found.id != model.id:
            metadata = {self.field: value}
            raise errors.resource_exists(self.resource, **metadata)


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

    def __init__(self, field, *validators):
        self.field = field
        self.validators = validators

    def validate(self, model):
        value = getattr(model, self.field)
        if value is not None:
            for validator in self.validators:
                validator.validate(model)


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


class ValidationAssociation(object):

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


class BaseExtensionRangeMixin(object):

    def _exten_in_range(self, exten, context_ranges):
        return any(context_range.in_range(exten)
                   for context_range in context_ranges)

    def _is_pattern(self, exten):
        return exten.startswith('_')
