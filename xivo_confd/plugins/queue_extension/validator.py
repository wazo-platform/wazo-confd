# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao_module

from xivo_confd.helpers.validator import (
    BaseExtensionRangeMixin,
    ValidatorAssociation,
    ValidationAssociation,
)


class QueueExtensionAssociationValidator(ValidatorAssociation, BaseExtensionRangeMixin):

    def __init__(self, context_dao):
        self._context_dao = context_dao

    def validate(self, queue, extension):
        self.validate_queue_not_already_associated(queue)
        self.validate_extension_not_already_associated(extension)
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_extension_is_in_internal_context(extension)
        self.validate_exten_is_in_context_queue_range(extension)

    def validate_queue_not_already_associated(self, queue):
        if queue.extensions:
            raise errors.resource_associated('Queue', 'Extension',
                                             queue_id=queue.id,
                                             extension_id=queue.extensions[0].id)

    def validate_extension_not_already_associated(self, extension):
        if extension.queue:
            raise errors.resource_associated('Queue', 'Extension',
                                             queue_id=extension.queue.id,
                                             extension_id=extension.id)

    def validate_extension_not_associated_to_other_resource(self, extension):
        if not (extension.type == 'user' and extension.typeval == '0'):
            raise errors.resource_associated('Extension',
                                             extension.type,
                                             extension_id=extension.id,
                                             associated_id=extension.typeval)

    def validate_extension_is_in_internal_context(self, extension):
        context = self._context_dao.get_by_name(extension.context)
        if context.type != 'internal':
            raise errors.unhandled_context_type(context.type,
                                                extension.context,
                                                id=extension.id,
                                                context=extension.context)

    def validate_exten_is_in_context_queue_range(self, extension):
        if self._is_pattern(extension.exten):
            return

        context = self._context_dao.get_by_name(extension.context)
        if not self._exten_in_range(extension.exten, context.queue_ranges):
            raise errors.outside_context_range(extension.exten, extension.context)


def build_validator():
    return ValidationAssociation(
        association=[QueueExtensionAssociationValidator(context_dao_module)],
    )
