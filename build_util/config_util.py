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

def load_config_file(filename, config_actions):
    tag = None
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            for line in f:
                stripped_line = line.rstrip()

                tag_match = re.match('\[(\w+)\]', stripped_line)
                if not stripped_line:
                    continue #skip blank line
                elif stripped_line.startswith('#'):
                    continue #skip comment line
                elif tag_match is not None:
                    tag = tag_match.group(1)
                else:
                    parts = re.split('\s*([\+:]?=)\s*', stripped_line, 1)
                    key = parts[0]
                    operation = parts[1]
                    value = parts[2]

                    if key.startswith('\t'):
                        key = key.lstrip()
                    else:
                        tag = None
                    config_actions.append((tag, (key, operation, value)))



def AssignOperation(d, key, value):
    d[key] = parse_value(value)

def AddOperation(d, key, value):
    collection = d.get(key)
    collection_values = [parse_value(part.strip()) for part in value.split(',')]
    if collection is None:
        raise Exception('no collection defined: '+key)
    elif type(collection) is set:
        d[key].update(collection_values)
    elif type(collection) is list:
        d[key].extend(collection_values)
    else:
        raise Exception('unknown collection type: ' + str(type(collection)) + ' in ' + key)

def DefineOperation(d, key, value):
    if value == 'set':
        d[key] = set()
    elif value == 'list':
        d[key] = list()
    else:
        raise Exception('Unknown type: '+value + ' for ' + key)

def parse_operation(s):
    if s == '=':
        return AssignOperation
    elif s == '+=':
        return AddOperation
    elif s == ':=':
        return DefineOperation
    else:
        raise Exception('Unknown operation: '+s)


def evaluate_config(config_actions, config_dict):
    remaining_actions = []
    for action in config_actions:
        tag = action[0]
        key = action[1][0]
        operation = parse_operation(action[1][1])
        value = action[1][2]

        if tag is None or tag in config_dict['tags']:
            operation(config_dict, key, value)
        else:
            remaining_actions.append(action)

    # recursivly apply actions until no more actions are applied
    if len(remaining_actions) > 0 and len(remaining_actions) != len(config_actions):
        evaluate_config(remaining_actions, config_dict)

def load_configs(filenames):
    with logger.trylog('loading configuration'):
        config_actions = []
        for filename in filenames:
            load_config_file(filename, config_actions)
        config_dict = dict()
        evaluate_config(config_actions, config_dict)

        config_dict['system.distributor_id'] = execute_with_stdout(['lsb_release', '-is']).strip()
        config_dict['system.codename'] = execute_with_stdout(['lsb_release', '-cs']).strip()
        config_dict['system.processor'] = execute_with_stdout(['uname', '-p']).strip()

        with logger.frame('loaded config', logger.SUCCESS):
            for key in sorted(config_dict):
                logger.log(key + ' = ' + str(config_dict[key]))
        return Config(config_dict, '')
