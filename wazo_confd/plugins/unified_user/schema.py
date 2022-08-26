# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.mallow import Nested
from xivo import mallow_helpers as mallow

BaseSchema = mallow.Schema


class UnifiedUserSchema(BaseSchema):
    user = Nested(
        'wazo_confd.plugins.unified_user.user_schema.UserXivoSchemaNullable',
        required=True,
        many=False,
    )

    @classmethod
    def _flatten(cls, iterable_of_iterable):
        for item in iterable_of_iterable:
            try:
                itercheck = iter(item)
                yield from cls._flatten(itercheck)
            except TypeError:
                yield item
