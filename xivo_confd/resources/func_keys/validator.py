# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

import re

from collections import Counter

from xivo_confd.helpers.validator import Validator, GetResource, \
    ResourceExists, MissingFields, ValidationGroup

from xivo_dao.helpers import errors
from xivo_dao.resources.agent import dao as agent_dao
from xivo_dao.resources.bsfilter import dao as bsfilter_dao
from xivo_dao.resources.conference import dao as conference_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.features import dao as feature_dao
from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.paging import dao as paging_dao
from xivo_dao.resources.queue import dao as queue_dao
from xivo_dao.resources.user import dao as user_dao


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
        for pos, funckey in template.keys.iteritems():
            self.funckey_validator.validate(funckey)


class FuncKeyValidator(Validator):

    LABEL_INVALID_CHARS = "\r\n\t;"

    def __init__(self, destinations):
        self.destinations = destinations

    def validate(self, funckey):
        self.validate_label(funckey)
        self.validate_destination(funckey)

    def validate_label(self, funckey):
        if funckey.label is not None:
            for char in funckey.label:
                if char in self.LABEL_INVALID_CHARS:
                    raise errors.wrong_type('label',
                                            "string without invalid characters (\\n \\r \\t ;)",
                                            label=funckey.label)

    def validate_destination(self, funckey):
        dest_type = funckey.destination.type
        if dest_type not in self.destinations:
            raise errors.invalid_destination_type(dest_type)
        for validator in self.destinations[dest_type]:
            validator.validate(funckey.destination)


class ServiceValidator(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, destination):
        extensions = self.dao.find_all_service_extensions()
        all_services = [e.service for e in extensions]
        service = destination.service

        if service not in all_services:
            raise errors.param_not_found('service', service)


class ForwardValidator(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, destination):
        extensions = self.dao.find_all_forward_extensions()
        all_forwards = [e.forward for e in extensions]
        forward = destination.forward

        if forward not in all_forwards:
            raise errors.param_not_found('forward', forward)


class TransferValidator(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, destination):
        extensions = self.dao.find_all_transfer_extensions()
        all_transfers = [e.transfer for e in extensions]
        transfer = destination.transfer

        if transfer not in all_transfers:
            raise errors.param_not_found('transfer', transfer)


class AgentActionValidator(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, destination):
        extensions = self.dao.find_all_agent_action_extensions()
        all_actions = [e.action for e in extensions]
        action = destination.action

        if action not in all_actions:
            raise errors.param_not_found('action', action)


class ParkPositionValidator(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, destination):
        min_pos, max_pos = self.dao.find_park_position_range()
        position = destination.position

        if not min_pos <= position <= max_pos:
            raise errors.outside_park_range(position, min=min_pos, max=max_pos)


class BSFilterValidator(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, user, funckey):
        if funckey.destination.type != 'bsfilter':
            return

        member_ids = [filter_member.member_id
                      for filter_member in self.dao.find_all_by_member_id(user.id)]
        if not member_ids:
            raise errors.missing_association('User', 'BSFilter', user_id=user.id)


def build_validators():
    destination_validators = {
        'user': [GetResource('user_id', user_dao.get, 'User')],
        'group': [ResourceExists('group_id', group_dao.exists, 'Group')],
        'queue': [ResourceExists('queue_id', queue_dao.exists, 'Queue')],
        'conference': [ResourceExists('conference_id', conference_dao.exists, 'Conference')],
        'custom': [],
        'service': [ServiceValidator(extension_dao)],
        'forward': [ForwardValidator(extension_dao)],
        'transfer': [TransferValidator(feature_dao)],
        'agent': [AgentActionValidator(extension_dao),
                  ResourceExists('agent_id', agent_dao.exists, 'Agent')],
        'park_position': [ParkPositionValidator(feature_dao)],
        'parking': [],
        'onlinerec': [],
        'paging': [ResourceExists('paging_id', paging_dao.exists, 'Paging')],
        'bsfilter': [ResourceExists('filter_member_id', bsfilter_dao.filter_member_exists, 'FilterMember')],
    }

    funckey_validator = FuncKeyValidator(destination_validators)
    mapping_validator = FuncKeyMappingValidator(funckey_validator)
    similar_validator = SimilarFuncKeyValidator()

    required_validator = MissingFields()
    private_template_validator = PrivateTemplateValidator()

    return ValidationGroup(common=[required_validator, mapping_validator, similar_validator],
                           delete=[private_template_validator])
