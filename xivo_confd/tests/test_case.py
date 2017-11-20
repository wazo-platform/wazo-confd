# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest


class TestCase(unittest.TestCase):

    def assertNotCalled(self, callee):
        self.assertEqual(callee.call_count, 0,
                         "%s was called %d times" % (callee, callee.call_count))
