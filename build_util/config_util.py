import os
import re

class Config(object):
    def __init__(self, d, prefix):
        self._d = d
        self._prefix = prefix
    def __getattr__(self, name):
        key = self._prefix+name
        if key in self._d:
            return self._d[key]
        elif len(filter(lambda key: key.startswith(key), self._d)) > 0:
            return Config(self._d, key+'.')
        else:
            return None

def load_config_file(filename, config_dict):
    config = dict()
    with open(filename, 'r') as f:
        for line in f:
            stripped_line = line.strip()

            if not stripped_line:
                continue #skip blank line
            elif stripped_line.startswith('#'):
                continue #skip comment line
            
            parts = re.split('\s*([\+:]?=)\s*', stripped_line, 1)
            
            if parts[1] == '=':
                config_dict[parts[0]] = parts[2]
            elif parts[1] == '+=':
                collection = config_dict.get(parts[0])
                if collection is None:
                    print 'no collection defined'
                elif type(collection) is set:
                    config_dict[parts[0]].add(parts[2])
                elif type(collection) is list:
                    config_dict[parts[0]].append(parts[2])
                else:
                    print 'unknown collection type: ' + str(type(collection))
            elif parts[1] == ':=':
                if parts[2] == 'set':
                    config_dict[parts[0]] = set()
                elif parts[2] == 'list':
                    config_dict[parts[0]] = list()
                else:
                    print 'Unknown type: '+parts[2]

def load_configs(filenames):
    config_dict = dict()
    for filename in filenames:
        load_config_file(filename, config_dict)

    print 'loaded config: '+str(config_dict)
    return Config(config_dict, '')
