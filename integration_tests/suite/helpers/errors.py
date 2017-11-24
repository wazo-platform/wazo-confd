# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from functools import partial
from hamcrest import assert_that, has_items, has_entries, instance_of, contains_string

import re


class RegexError(object):

    NO_ERROR_FOUND = "{} did not match on {}"
    NO_MATCH = "{} not found in error {}"

    def __init__(self, regex, *items, **group):
        self.regex = regex
        self.items = items
        self.group = group

    def __str__(self):
        return "<{} {} {}>".format(self.__class__.__name__, self.regex.pattern, self.group)

    def __repr__(self):
        return str(self)

    def assert_match(self, errors):
        match = self.find_error(errors)
        if self.items:
            assert_that(match.groups(),
                        has_items(*self.items),
                        self.NO_MATCH.format(self.items, errors))
        if self.group:
            assert_that(match.groupdict(),
                        has_entries(self.group),
                        self.NO_MATCH.format(self.items, errors))

    def find_error(self, errors):
        assert_that(errors, instance_of(list), "Expecting a list of errors")
        for message in errors:
            match = self.regex.search(message)
            if match:
                return match
        raise AssertionError(self.NO_ERROR_FOUND.format(self.regex.pattern, errors))


class SequenceError(RegexError):

    def assert_match(self, errors):
        match = self.find_error(errors)
        matched_items = match.group(1)
        for item in self.items:
            assert_that(matched_items,
                        contains_string(item),
                        self.NO_MATCH.format(self.items, errors))


def build_error(raw_regex, builder=RegexError):
    regex = re.compile(raw_regex)
    return partial(builder, regex)


wrong_type = build_error(r"field '(?P<field>[^']+)': wrong type. Should be an? (?P<type>[\w-]+( [\w-]+)*)")
not_found = build_error(r"(?P<resource>\w+) was not found")
missing_association = build_error(r"(?P<left>\w+) must be associated with a (?P<right>\w+)")
resource_exists = build_error(r"(?P<resource>\w+) already exists")
resource_associated = build_error(r"(?P<left>\w+) is associated with a (?P<right>\w+( \w+)*)")
unknown_parameters = build_error(r"unknown parameters: ((\w+)(, (\w+))*)", SequenceError)
missing_parameters = build_error(r"missing parameters: ((\w+)(, (\w+))*)", SequenceError)
