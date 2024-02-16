# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import defaultdict
from operator import attrgetter, itemgetter

from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.extension import dao as extension_dao


class Range:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def contains(self, exten):
        return self.start <= exten <= self.end

    def split_at(self, exten):
        if exten < self.start:
            return [self]
        if exten > self.end:
            return [self]
        if exten == self.start:
            return [Range(start=self.plus(range.start, 1), end=self.end)]
        if exten == self.end:
            return [Range(start=self.start, end=self.minus(range.end, 1))]
        if self.start < exten < self.end:
            return [
                Range(start=self.start, end=self.minus(exten, 1)),
                Range(start=self.plus(exten, 1), end=self.end),
            ]

    def split_from_search(self, search):
        matching = False
        start = None
        end = None

        for exten in self._generate_extens():
            if search in exten:
                if matching is False:
                    start = exten
                elif matching is True:
                    end = exten
                matching = True
            else:
                if matching is True:
                    yield Range(start=start, end=end or start)
                    start = None
                    end = None
                    matching = False

    def _generate_extens(self):
        exten_len = len(self.start)
        first = int(self.start)
        last = int(self.end)

        for n in range(first, last + 1):
            yield str(n).rjust(exten_len, '0')

    @staticmethod
    def plus(exten, n):
        length = len(exten)
        return str(int(exten) + n).rjust(length, '0')

    @staticmethod
    def minus(exten, n):
        length = len(exten)
        return str(int(exten) - n).rjust(length, '0')

    def __str__(self):
        return f'Range({self.start}, {self.end})'

    def __repr__(self):
        return self.__str__()


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
        configured_ranges = self._extract_ranges(self._context, range_type)
        i = 0
        while i < len(configured_ranges):
            range = configured_ranges[i]
            for exten in self._used_extensions:
                if range.contains(exten):
                    del configured_ranges[i]  # Replaces i++
                    new_ranges = range.split_at(exten)
                    j = 0
                    for j, new in enumerate(new_ranges):
                        configured_ranges.insert(i + j, new)
                    if j > 0:
                        i += j - 1
            i += 1

        if self._search:
            filtered_ranges = []
            for range in configured_ranges:
                for new_range in range.split_from_search(self._search):
                    filtered_ranges.append(new_range)
        else:
            filtered_ranges = configured_ranges

        return [{'start': r.start, 'end': r.end} for r in filtered_ranges]

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
            return [Range(r.start, r.end) for r in context.user_ranges]
        elif range_type == 'group':
            return [Range(r.start, r.end) for r in context.group_ranges]
        elif range_type == 'queue':
            return [Range(r.start, r.end) for r in context.queue_ranges]
        elif range_type == 'conference':
            return [Range(r.start, r.end) for r in context.conference_room_ranges]
        elif range_type == 'incall':
            return [Range(r.start, r.end) for r in context.incall_ranges]
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
            previous = None
            for current in sorted(ranges_by_len[length], key=attrgetter('start')):
                if previous is None:
                    previous = current
                else:
                    if previous.end >= current.start:
                        previous = Range(
                            start=previous.start, end=max(previous.end, current.end)
                        )
                    else:
                        yield previous
            yield current

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


class RangeMerger:
    def merge(self, ranges):
        ranges_by_len = defaultdict(list)
        for range in ranges:
            ranges_by_len[len(range['start'])].append(range)

        for length in sorted(ranges_by_len.keys()):
            previous = None
            for current in sorted(ranges_by_len[length], key=itemgetter('start')):
                if previous is None:
                    previous = current
                else:
                    if previous['end'] >= current['start']:
                        previous = {
                            'start': min(previous['start'], current['start']),
                            'end': max(previous['end'], current['end']),
                        }
                    else:
                        yield previous
                        previous = current
            yield previous


class ContextRangeService:
    def __init__(self, context_dao, extension_dao):
        self._context_dao = context_dao
        self._extension_dao = extension_dao

    def search(self, context_id, range_type, tenant_uuids=None, **parameters):
        context = self._context_dao.get(context_id, tenant_uuids=tenant_uuids)

        filter = RangeFilter(context, self._extension_dao, **parameters)
        paginator = RangePaginator(**parameters)
        sorter = RangeSorter(**parameters)
        merger = RangeMerger()

        ranges = filter.get_ranges(range_type)
        merged_ranges = list(merger.merge(ranges))
        count = len(merged_ranges)
        sorted_ranges = sorter.sort(merged_ranges)
        paginated_ranges = paginator.paginate(sorted_ranges)

        return count, paginated_ranges


def build_service():
    return ContextRangeService(context_dao, extension_dao)
