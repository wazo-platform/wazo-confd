# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.extension import dao as extension_dao

logger = logging.getLogger(__name__)


class RangeFilter:
    def __init__(self, context, extension_dao, available=None, search=None, **kwargs):
        self._context = context
        self._extension_dao = extension_dao
        self._available = available
        self._search = search
        self._used_extensions = set()

        if self._available:
            configured_extens = self._extension_dao.find_all_by(context=context.name)
            self._used_extensions = set(e.exten for e in configured_extens)

    def get_ranges(self, range_type):
        ranges = self._extract_ranges(self._context, range_type)
        unfiltered_extens = self._list_exten_from_ranges(ranges)
        filtered_extens = (
            exten for exten in unfiltered_extens if self._include_exten(exten)
        )
        filtered_ranges = list(self._ranges_from_extens(filtered_extens))
        count = len(filtered_ranges)
        return filtered_ranges, count

    def _include_exten(self, exten):
        if self._available:
            if exten in self._used_extensions:
                return False
        if self._search:
            if self._search not in exten:
                return False
        return True

    def _extract_ranges(self, context, range_type):
        if range_type == 'user':
            return context.user_ranges
        elif range_type == 'group':
            return context.group_ranges
        elif range_type == 'queue':
            return context.queue_ranges
        elif range_type == 'conference':
            return context.conference_room_ranges
        elif range_type == 'incall':
            return context.incall_ranges
        else:
            assert False, f'{range_type} is not supported'

    @staticmethod
    def _list_exten_from_ranges(ranges):
        for r in ranges:
            start = r.start
            end = r.end
            length = len(start)
            for exten in range(int(start), int(end) + 1):
                yield str(exten).rjust(length, '0')

    @staticmethod
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


class RangePaginator:
    def __init__(self, limit=None, offset=0, **kwargs):
        self._limit = limit
        self._offset = offset

    def paginate(self, ranges):
        if self._limit is None:
            return ranges[self._offset :]
        else:
            return ranges[self._offset : self._offset + self._limit]


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
        filter = RangeFilter(context, self._extension_dao, **parameters)
        paginator = RangePaginator(**parameters)
        ranges, count = filter.get_ranges(range_type)
        paginated_ranges = paginator.paginate(ranges)
        return count, paginated_ranges


def build_service():
    return ContextRangeService(context_dao, extension_dao)
