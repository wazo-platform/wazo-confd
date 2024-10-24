# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao.resources.phone_number import dao
from xivo_dao.alchemy.phone_number import PhoneNumber
from xivo_dao.helpers.errors import ResourceError
from wazo_confd.helpers.resource import CRUDService

from .utils import PhoneNumberRangeSpec, generate_phone_number_range
from .notifier import build_notifier
from .validator import build_validator


logger = logging.getLogger(__name__)


class PhoneNumberService(CRUDService):
    dao: dao

    def __init__(self, dao, validator, notifier):
        super().__init__(dao, validator, notifier)

    def find_all_by(self, **criteria) -> list[PhoneNumber]:
        return self.dao.find_all_by(**criteria)

    def create_range(
        self, range_spec: PhoneNumberRangeSpec, tenant_uuids: list[str]
    ) -> tuple[list[PhoneNumber], list[PhoneNumber]]:
        register_phone_numbers = []
        _redundant_phone_numbers = []
        for number in generate_phone_number_range(
            range_spec.start_number, range_spec.end_number
        ):
            try:
                phone_number = self.create(
                    PhoneNumber(
                        number=number,
                        tenant_uuid=tenant_uuids[0],
                    )
                )
            except ResourceError as ex:
                if "already exists" in str(ex):
                    _redundant_phone_numbers.append(number)
                    continue
                else:
                    raise

            register_phone_numbers.append(phone_number)

        redundant_phone_numbers = self.find_all_by(
            number_in=_redundant_phone_numbers,
            tenant_uuids=tenant_uuids,
        )

        logger.info(
            'Registered %d new phone numbers (out of %d total) from range (%s - %s)',
            len(register_phone_numbers),
            len(register_phone_numbers) + len(redundant_phone_numbers),
            range_spec.start_number,
            range_spec.end_number,
        )
        return register_phone_numbers, redundant_phone_numbers


def build_service():
    return PhoneNumberService(dao, build_validator(), build_notifier())
