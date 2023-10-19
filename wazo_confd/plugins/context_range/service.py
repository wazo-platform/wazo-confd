# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.extension import dao as extension_dao

logger = logging.getLogger(__name__)


class ContextRangeService:
    def __init__(self, context_dao, extension_dao):
        self._context_dao = context_dao
        self._extension_dao = extension_dao

    def search(self, context_id, range_type, parameters, tenant_uuids=None):
        logger.info(
            'search %s %s %s %s',
            context_id, range_type, parameters, tenant_uuids,
        )

        context = self._context_dao.get(context_id)
        if range_type == 'user':
            range = context.user_ranges
        elif range_type == 'group':
            range = context.group_ranges
        elif range_type == 'queue':
            range = context.queue_ranges
        elif range_type == 'conference':
            range = context.conference_room_ranges
        elif range_type == 'incall':
            range = context.incall_ranges
        else:
            assert False, f'{range_type} is not supported'

        if parameters['available']:
            extensions = self._extension_dao.find_all_by(context=context.name)
            used_extensions = set(e.exten for e in extensions)
        else:
            used_extensions = set()

        def exten_filter(exten):
            term = parameters.get('search')
            if term:
                if term not in exten:
                    return False
            return exten not in used_extensions

        filtered_extensions = (
            exten for exten in _list_exten_from_ranges(range)
            if exten_filter(exten)
        )
        ranges = _ranges_from_extens(filtered_extensions)

        response = list(ranges)

        return len(response), response


def build_service():
    return ContextRangeService(context_dao, extension_dao)


def _list_exten_from_ranges(ranges):
    for r in ranges:
        start = r.start
        end = r.end
        length = len(start)
        for exten in range(int(start), int(end) + 1):
            yield str(exten).rjust(length, '0')


def _ranges_from_extens(extensions):
    start, previous = None, None
    for exten in extensions:
        if not start:
            start = exten
        if previous:
            increment = int(exten) - int(previous)
            len_diff = len(exten) - len(previous) > 0
            if increment > 1 or len_diff:
                yield {'start': start, 'end': previous}
                start, previous = exten, None
        previous = exten
    yield {'start': start, 'end': previous}
