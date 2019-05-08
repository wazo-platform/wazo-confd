# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import Counter

from xivo_dao.helpers import errors
from xivo_dao.resources.agent import dao as agent_dao
from xivo_dao.resources.call_filter import dao as call_filter_dao
from xivo_dao.resources.conference import dao as conference_dao
from xivo_dao.resources.features import dao as feature_dao
from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.paging import dao as paging_dao
from xivo_dao.resources.queue import dao as queue_dao
from xivo_dao.resources.user import dao as user_dao

from xivo_confd.helpers.validator import (
    Validator,
    GetResource,
    ResourceExists,
    ValidationGroup,
)


class PrivateTemplateValidator(Validator):

    def validate(self, template):
        if template.private:
            raise errors.not_permitted("Deleting private templates is not allowed",
                                       template_id=template.id)


class SimilarFuncKeyValidator(Validator):

    def validate(self, template):
        counter = Counter(funckey.hash_destination()
                          for funckey in template.keys.values())
        if len(counter) > 0:
            destination, counts = counter.most_common(1)[0]
            if counts > 1:
                args = dict(destination)
                raise errors.resource_exists('destination', **args)


class FuncKeyMappingValidator(Validator):

    def __init__(self, funckey_validator):
        self.funckey_validator = funckey_validator

    def validate(self, template):
        for pos, funckey in template.keys.items():
            self.funckey_validator.validate(funckey)


class FuncKeyValidator(Validator):

    INVALID_CHARS = "\n\r\t;"
    INVALID_CHARS_MSG = "string without special characters (\\n \\r \\t ;)"

    def validate_text(self, text, field):
        if text is not None:
            for char in self.INVALID_CHARS:
                if char in text:
                    raise errors.wrong_type(field, self.INVALID_CHARS_MSG, **{field: text})


class FuncKeyModelValidator(FuncKeyValidator):

    def __init__(self, destinations):
        self.destinations = destinations

    def validate(self, funckey):
        self.validate_text(funckey.label, 'label')
        self.validate_destination(funckey)

    def validate_destination(self, funckey):
        dest_type = funckey.destination.type
        if dest_type not in self.destinations:
            raise errors.invalid_destination_type(dest_type)
        for validator in self.destinations[dest_type]:
            validator.validate(funckey.destination)


class ForwardValidator(FuncKeyValidator):

    def validate(self, destination):
        self.validate_text(destination.exten, 'exten')


class ParkPositionValidator(FuncKeyValidator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, destination):
        min_pos, max_pos = self.dao.find_park_position_range()
        position = destination.position

        if not min_pos <= position <= max_pos:
            raise errors.outside_park_range(position, min=min_pos, max=max_pos)


class CustomValidator(FuncKeyValidator):

    def validate(self, destination):
        self.validate_text(destination.exten, 'exten')


class BSFilterValidator(FuncKeyValidator):

    def validate(self, user, funckey):
        if funckey.destination.type != 'bsfilter':
            return

        if not (user.call_filter_recipients or user.call_filter_surrogates):
            raise errors.missing_association('User', 'BSFilter', user_id=user.id)


def build_validator():
    destination_validators = {
        'agent': [GetResource('agent_id', agent_dao.get, 'Agent')],
        'bsfilter': [ResourceExists('filter_member_id', call_filter_dao.member_exists, 'FilterMember')],
        'conference': [ResourceExists('conference_id', conference_dao.exists, 'Conference')],
        'custom': [CustomValidator()],
        'forward': [ForwardValidator()],
        'group': [GetResource('group_id', group_dao.get, 'Group')],
        'groupmember': [GetResource('group_id', group_dao.get, 'Group')],
        'onlinerec': [],
        'paging': [GetResource('paging_id', paging_dao.get, 'Paging')],
        'park_position': [ParkPositionValidator(feature_dao)],
        'parking': [],
        'queue': [GetResource('queue_id', queue_dao.get, 'Queue')],
        'service': [],
        'transfer': [],
        'user': [GetResource('user_id', user_dao.get, 'User')],
    }

    funckey_validator = FuncKeyModelValidator(destination_validators)
    mapping_validator = FuncKeyMappingValidator(funckey_validator)
    similar_validator = SimilarFuncKeyValidator()

    private_template_validator = PrivateTemplateValidator()

    return ValidationGroup(common=[mapping_validator, similar_validator],
                           delete=[private_template_validator])


def build_validator_bsfilter():
    return BSFilterValidator()
