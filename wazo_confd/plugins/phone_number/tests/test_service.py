import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_confd.plugins.phone_number.utils import PhoneNumberRangeSpec
from wazo_confd.plugins.phone_number.service import PhoneNumberService
from xivo_dao.helpers.errors import ResourceError


class TestPhoneNumberService(unittest.TestCase):
    def setUp(self) -> None:
        self.dao = Mock(
            find_all_by=Mock(return_value=[]),
            create=Mock(return_value=Mock()),
            delete=Mock(return_value=Mock()),
            find_by=Mock(return_value=Mock()),
        )
        self.service = PhoneNumberService(
            dao=self.dao, validator=Mock(), notifier=Mock()
        )

    def test_create_range(self):
        created_numbers, redundant_numbers = self.service.create_range(
            range_spec=PhoneNumberRangeSpec(
                start_number='15550000000',
                end_number='15550000999',
            ),
            tenant_uuids=['1234'],
        )

        assert (
            created_numbers and len(created_numbers) == 1000
        ), f'len(created_numbers)={len(created_numbers)}'

        assert not redundant_numbers

    def test_create_range_idempotency(self):
        redundant_numbers = [
            Mock(
                number=str(number),
                uuid=uuid4(),
                caller_id_name=None,
                tenant_uuid='1234',
            )
            for number in range(15550000500, 15550001000)
        ]
        self.dao.find_all_by.return_value = redundant_numbers

        def reject_redundant_numbers(resource):
            if resource.number in set(num.number for num in redundant_numbers):
                raise ResourceError("number already exists")
            return resource

        self.dao.create.side_effect = reject_redundant_numbers

        created_numbers, redundant_numbers = self.service.create_range(
            range_spec=PhoneNumberRangeSpec(
                start_number='15550000000',
                end_number='15550000999',
            ),
            tenant_uuids=['1234'],
        )
        assert (
            len(created_numbers) == 500
        ), f'len(created_numbers)={len(created_numbers)}'
        assert len(redundant_numbers) == 500
