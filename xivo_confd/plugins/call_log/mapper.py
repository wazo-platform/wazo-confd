# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+


def to_api(call_log):
    result = {}
    result['Call Date'] = call_log.date.isoformat()
    result['Caller'] = '%s (%s)' % (call_log.source_name, call_log.source_exten)
    result['Called'] = call_log.destination_exten
    if call_log.date_answer and call_log.date_end:
        result['Period'] = _format_duration(call_log.date_end - call_log.date_answer)
    else:
        result['Period'] = 0
    result['user Field'] = call_log.user_field or ''
    return result


def _format_duration(duration):
    return str(int(round(duration.total_seconds())))
