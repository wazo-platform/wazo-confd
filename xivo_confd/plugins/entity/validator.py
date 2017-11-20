# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.validator import (UniqueField,
                                          Validator,
                                          ValidationGroup)
from xivo_dao.helpers import errors
from xivo_dao.resources.entity import dao as entity_dao
from xivo_dao.resources.user import dao as user_dao

from xivo_confd.database import call_pickup as call_pickup_dao
from xivo_confd.database import call_filter as call_filter_dao
from xivo_confd.database import context as context_dao
from xivo_confd.database import schedule as schedule_dao


class DBValidator(Validator):

    def __init__(self, dao):
        self.dao = dao


class NoUserAssociated(DBValidator):

    def validate(self, entity):
        user = self.dao.find_by(entityid=entity.id)
        if user:
            raise errors.resource_associated('Entity',
                                             'User',
                                             entity_id=user.entity_id,
                                             user_id=user.id)


class NoCallPickupAssociated(DBValidator):

    def validate(self, entity):
        call_pickup = self.dao.find_by(entity_id=entity.id)
        if call_pickup:
            raise errors.resource_associated('Entity',
                                             'CallPickup',
                                             entity_id=entity.id,
                                             call_pickup_id=call_pickup.id)


class NoCallFilterAssociated(DBValidator):

    def validate(self, entity):
        call_filter = self.dao.find_by(entity_id=entity.id)
        if call_filter:
            raise errors.resource_associated('Entity',
                                             'CallFilter',
                                             entity_id=entity.id,
                                             call_filter_id=call_filter.id)


class NoContextAssociated(DBValidator):

    def validate(self, entity):
        context = self.dao.find_by(entity=entity.name)
        if context:
            raise errors.resource_associated('Entity',
                                             'Context',
                                             entity_id=entity.id,
                                             context_name=context.name)


class NoScheduleAssociated(DBValidator):

    def validate(self, entity):
        schedule = self.dao.find_by(entity_id=entity.id)
        if schedule:
            raise errors.resource_associated('Entity',
                                             'Schedule',
                                             entity_id=entity.id,
                                             schedule_id=schedule.id)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('name',
                        lambda name: entity_dao.find_by(name=name),
                        'Entity')
        ],
        delete=[
            NoUserAssociated(user_dao),
            NoCallPickupAssociated(call_pickup_dao),
            NoCallFilterAssociated(call_filter_dao),
            NoScheduleAssociated(schedule_dao),
            NoContextAssociated(context_dao)

        ],
    )
