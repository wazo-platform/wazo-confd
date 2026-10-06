# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Literal

# `default` defers to the dialplan, also when nothing was ever stored, and is
# only meaningful for the default caller ID, as is `custom`: reported, never
# accepted, when the stored value is no longer available to the user.
CallerIDType = Literal['main', 'associated', 'anonymous', 'shared', 'default', 'custom']
