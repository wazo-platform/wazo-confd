# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import defaultdict
from operator import attrgetter, itemgetter

from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.extension import dao as extension_dao


class RangeFilter:
    def __init__(
        self, context, extension_dao, availability=None, search=None, **kwargs
    ):
        self._context = context
        self._extension_dao = extension_dao
        self._availability = availability
        self._search = search
        self._used_extensions = set()

        if self._availability == 'available':
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
        if self._availability == 'available':
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

    @classmethod
    def _list_exten_from_ranges(cls, ranges):
        listed_extens = set()
        for r in cls._sort_ranges(ranges):
            start = r.start
            end = r.end
            length = len(start)
            for exten in range(int(start), int(end) + 1):
                formatted_exten = str(exten).rjust(length, '0')
                if formatted_exten in listed_extens:
                    continue
                listed_extens.add(formatted_exten)
                yield formatted_exten

    @staticmethod
    def _sort_ranges(ranges):
        ranges_by_len = defaultdict(list)
        for range in ranges:
            ranges_by_len[len(range.start)].append(range)

        for length in sorted(ranges_by_len.keys()):
            for range in sorted(ranges_by_len[length], key=attrgetter('start')):
                yield range

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
        if start:
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


class RangeSorter:
    def __init__(self, order=None, direction='asc', **kwargs):
        self._should_sort = order is not None
        if self._should_sort:
            self._key = itemgetter(order)
            self._reverse = direction == 'desc'

    def sort(self, ranges):
        if not self._should_sort:
            return ranges
        return sorted(ranges, key=self._key, reverse=self._reverse)


class ContextRangeService:
    def __init__(self, context_dao, extension_dao):
        self._context_dao = context_dao
        self._extension_dao = extension_dao

    def search(self, context_id, range_type, tenant_uuids=None, **parameters):
        context = self._context_dao.get(context_id, tenant_uuids=tenant_uuids)

        filter = RangeFilter(context, self._extension_dao, **parameters)
        paginator = RangePaginator(**parameters)
        sorter = RangeSorter(**parameters)

        ranges, count = filter.get_ranges(range_type)
        sorted_ranges = sorter.sort(ranges)
        paginated_ranges = paginator.paginate(sorted_ranges)

        return count, paginated_ranges


def build_service():
    return ContextRangeService(context_dao, extension_dao)
