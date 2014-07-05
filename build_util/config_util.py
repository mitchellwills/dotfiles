import os
import re
import subprocess
import logger

def execute_with_stdout(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out

def parse_value(val):
    if val.lower() == 'true':
        return True
    elif val.lower() == 'false':
        return False
    return val
    
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
                config_dict[parts[0]] = parse_value(parts[2])
            elif parts[1] == '+=':
                collection = config_dict.get(parts[0])
                collection_values = [parse_value(part.strip()) for part in parts[2].split(',')]
                if collection is None:
                    logger.error('no collection defined')
                elif type(collection) is set:
                    config_dict[parts[0]].update(collection_values)
                elif type(collection) is list:
                    config_dict[parts[0]].extend(collection_values)
                else:
                    logger.error('unknown collection type: ' + str(type(collection)))
            elif parts[1] == ':=':
                if parts[2] == 'set':
                    config_dict[parts[0]] = set()
                elif parts[2] == 'list':
                    config_dict[parts[0]] = list()
                else:
                    logger.error('Unknown type: '+parts[2])

def load_configs(filenames):
    with logger.frame('loading configuration'):
        config_dict = dict()
        for filename in filenames:
            load_config_file(filename, config_dict)

        config_dict['system.distributor_id'] = execute_with_stdout(['lsb_release', '-is']).strip()
        config_dict['system.codename'] = execute_with_stdout(['lsb_release', '-cs']).strip()

        with logger.frame('loaded config', logger.SUCCESS):
            for key in config_dict:
                logger.log(key + ' = ' + str(config_dict[key]))
        return Config(config_dict, '')
