# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from ..wait import _parse_cli_args


def test_no_args_leaves_port_unset():
    args = _parse_cli_args([])

    assert args.port is None


def test_port_argument_is_an_int():
    args = _parse_cli_args(['--port', '19486'])

    assert args.port == 19486
