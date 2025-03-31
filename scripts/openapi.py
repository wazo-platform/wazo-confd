#!/usr/bin/env python3
import sys

import yaml
from pkg_resources import iter_entry_points
from xivo.chain_map import ChainMap
from xivo.rest_api_helpers import load_all_api_specs

if __name__ == '__main__':
    for entrypoint in iter_entry_points('wazo_confd.plugins'):
        print(f'Entry point: {entrypoint.module_name}', file=sys.stderr)

    api_specs = []
    for api_spec in load_all_api_specs('wazo_confd.plugins', 'api.yml'):
        paths = api_spec.get('paths', {}).keys()
        for path in paths:
            print(f'Path: {path}', file=sys.stderr)
        api_specs.append(api_spec)
    api_spec = ChainMap(*api_specs)
    host = sys.argv[1] if len(sys.argv) > 1 else None
    if host:
        api_spec['host'] = host
    prefix = sys.argv[2] if len(sys.argv) > 2 else None
    if prefix:
        api_spec['schemes'] = ['https']
        base_path = api_spec.get('basePath', '')
        api_spec['basePath'] = f'{prefix}{base_path}'
    print(yaml.dump(dict(api_spec)))
