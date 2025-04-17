# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import contextlib


@contextlib.contextmanager
def context_group(*context_managers: contextlib.AbstractContextManager):
    with contextlib.ExitStack() as stack:
        yield [stack.enter_context(cm) for cm in context_managers]
