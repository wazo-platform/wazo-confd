# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def generate_access_feature(**params):
    params.setdefault('feature', 'phonebook')
    return add_access_feature(**params)


def add_access_feature(**params):
    print('Params: {}'.format(params))
    response = confd.access_features.post(params)
    return response.item


def delete_access_feature(access_feature_id, check=False):
    response = confd.access_features(access_feature_id).delete()
    if check:
        response.assert_ok()
