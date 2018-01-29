# -*- coding: UTF-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import (
    assert_that,
    contains_inanyorder,
    empty,
    equal_to,
    has_properties,
)

from ..model import SoundCategory, SoundFile, SoundFormat


class TestSoundCategory(unittest.TestCase):

    def test_add_file_with_same_name(self):
        original = SoundCategory(name='system', files=[
            SoundFile(name='hello', formats=[
                SoundFormat(language='en'),
                SoundFormat(language='en_US'),
            ]),
            SoundFile(name='bob'),
        ])
        other = SoundFile(name='hello', formats=[
            SoundFormat(language='en'),
            SoundFormat(language='fr_FR'),
        ])

        original.add_file(other)

        assert_that(original.files, contains_inanyorder(
            has_properties(name='hello', formats=contains_inanyorder(
                has_properties(language='en'),
                has_properties(language='en_US'),
                has_properties(language='fr_FR'),
            )),
            has_properties(name='bob', formats=empty()),
        ))

    def test_add_file_with_different_name(self):
        original = SoundCategory(name='system', files=[
            SoundFile(name='hello'),
            SoundFile(name='bob'),
        ])
        other = SoundFile(name='world')

        original.add_file(other)

        assert_that(original.files, contains_inanyorder(
            has_properties(name='hello'),
            has_properties(name='world'),
            has_properties(name='bob'),
        ))


class TestSoundFile(unittest.TestCase):

    def test_update_without_same_name(self):
        original = SoundFile(name='hello-world')
        other = SoundFile(name='bye-world', formats=[
            SoundFormat(language='fr_FR'),
        ])

        original.update(other)

        assert_that(original.formats, empty())

    def test_update_without_files(self):
        original = SoundFile(name='system')
        other = SoundFile(name='system')

        original.update(other)

        assert_that(original.formats, empty())

    def test_update(self):
        original = SoundFile(name='hello', formats=[
            SoundFormat(language='en'),
            SoundFormat(language='en_US'),
        ])
        other = SoundFile(name='hello', formats=[
            SoundFormat(language='en'),
            SoundFormat(language='fr_FR'),
        ])

        original.update(other)

        assert_that(original.formats, contains_inanyorder(
            has_properties(language='en'),
            has_properties(language='en_US'),
            has_properties(language='fr_FR'),
        ))


class TestSoundFormat(unittest.TestCase):

    def test_format_chosen_when_extension_format(self):
        result = SoundFormat(format_='foo', extension='bar')
        assert_that(result.format, equal_to('foo'))
        assert_that(result.extension, equal_to('foo'))

    def test_extension_with_None(self):
        result = SoundFormat(extension='')
        assert_that(result.format, equal_to(None))

    def test_extension_with_wav(self):
        result = SoundFormat(extension='wav')
        assert_that(result.format, equal_to('slin'))

    def test_extension_with_other(self):
        result = SoundFormat(extension='other_extension')
        assert_that(result.format, equal_to('other_extension'))

    def test_format_with_None(self):
        result = SoundFormat(format_=None)
        assert_that(result.extension, equal_to(''))

    def test_format_with_wav(self):
        result = SoundFormat(format_='slin')
        assert_that(result.extension, equal_to('wav'))

    def test_format_with_other(self):
        result = SoundFormat(format_='other_extension')
        assert_that(result.extension, equal_to('other_extension'))
