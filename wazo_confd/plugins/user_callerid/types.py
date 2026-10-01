# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Literal

CallerIDType = Literal['main', 'associated', 'anonymous', 'shared']

# `default` defers to the dialplan. `custom` and `unset` are only ever reported,
# never accepted: `custom` when the stored value is no longer available to the
# user, `unset` when nothing was ever stored. Unlike `default`, `unset` never
# applies the outcall caller ID: the dialplan presents the user's own.
CallerIDDefaultType = Literal[
    'main', 'associated', 'anonymous', 'shared', 'default', 'custom', 'unset'
]
