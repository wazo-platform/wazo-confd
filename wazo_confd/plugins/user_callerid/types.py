# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Literal

CallerIDType = Literal['main', 'associated', 'anonymous', 'shared']

# `default` defers to the dialplan. `custom` is only ever reported, never
# accepted: the stored value is no longer available to the user.
CallerIDDefaultType = Literal[
    'main', 'associated', 'anonymous', 'shared', 'default', 'custom'
]
