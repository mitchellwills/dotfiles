import os
import re
import subprocess
import logger

def execute_with_stdout(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out

def parse_value(val):
    if type(val) is not str:
        return val

    if val.lower() == 'true':
        return True
    elif val.lower() == 'false':
        return False
    return val

def parse_values(value):
    if type(value) == str:
        return [parse_value(part.strip()) for part in value.split(',')]
    elif type(value) == list:
        return value
    else:
        raise Exception('Unexpected input ' + value)

class Config(object):
    def __init__(self, prefix = '', store = dict()):
        self._prefix = prefix
        self._store = store
    def resolve(self, name):
        return self._prefix+name
    def __getattr__(self, name):
        key = self.resolve(name)
        if key in self._store:
            return self._store[key].get()
        elif len(filter(lambda x: x.startswith(key), self._store)) > 0:
            return Config(prefix = key+'.', store = self._store)
        else:
            return None
    def __setitem__(self, name, value):
        self.assign(name, value, None)
    def __getitem__(self, name):
        return self.__getattr__(name)
    def keys(self):
        subkeys = map(lambda key: key.replace(self._prefix, ''), filter(lambda k: k.startswith(self._prefix), self._store))
        subkeys = set(map(lambda key: key.split('.', 1)[0], subkeys))
        subkeys.discard('')
        return subkeys
    def ensure(self, name):
        self.assign(name+'.', 'ENSURE')
    def assign(self, name, value, priority=-1):
        key = self.resolve(name)
        if key not in self._store:
            self._store[key] = ConfigValue(key)
        self._store[key].assign(value, priority)

    def _get_collection(self, name):
        key = self.resolve(name)
        if key not in self._store:
            raise Exception('No value for ' + key)
        collection = self._store[key]
        if type(collection) is ConfigCollection:
            return self._store[key]
        else:
            raise Exception('Not a collection defined in ' + key + ', was a ' + str(type(collection)))

    def add(self, name, value, priority):
        self._get_collection(name).add(value, priority)
    def remove(self, name, value, priority):
        self._get_collection(name).remove(value, priority)

    def define(self, name, t):
        key = self.resolve(name)
        if key not in self._store:
            self._store[key] = ConfigCollection(key, t)
        else:
            raise Exception(key + ' already defined')

    def dump_store(self):
        with logger.frame('Config:', logger.SUCCESS):
            for key in sorted(self._store):
                logger.log(key + ' = ' + str(self._store[key].get()))


def parse_config_file(filename):
    config_actions = []
    tag = None
    prefix = ''
    previous_line_comment = None
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            first_line = True
            for line in f:
                stripped_line = line.rstrip()

                tag_match = re.match('\[([^\]]+)\]', stripped_line)
                if not stripped_line:
                    continue #skip blank line
                elif stripped_line.startswith('#'):
                    continue #skip comment line
                elif first_line and stripped_line.startswith(':'):
                    prefix = stripped_line.lstrip(':')+'.'
                    previous_line_comment = None
                    if previous_line_comment is not None:
                        raise Exception('key comment before prefix line')
                elif tag_match is not None:
                    tag = tag_match.group(1)
                    if previous_line_comment is not None:
                        raise Exception('key comment before tag line')
                elif stripped_line.startswith('%'):
                    previous_line_comment = stripped_line[1:].strip()
                else:
                    parts = re.split('\s*([\+:-]?=)\s*', stripped_line, 1)
                    key = parts[0]
                    operation = parts[1]
                    value = parts[2]

                    if key.startswith('\t'):
                        key = key.lstrip()
                    else:
                        tag = None
                    config_actions.append((tag, (prefix + key, operation, value)))
                    if previous_line_comment is not None:
                        config_actions.append((tag, (prefix + key + '.comment', '=', previous_line_comment)))
                    previous_line_comment = None
                first_line = False
    return config_actions


# A class that evaluates to the last assigned value
class ConfigValue(object):
    def __init__(self, key, default_value = None):
        self.key = key
        self.values = []
        if default_value is not None:
            self.values.append((value, -1))
    def assign(self, value, priority):
        if priority is None:
            if len(self.values) > 0:
                priority = self.values[0][1] + 1
            else:
                priority = 0
        self.values.append((parse_value(value), priority))
        self.values.sort(key=lambda x:x[1], reverse=True)
    def get(self):
        return self.values[0][0]

class ConfigSet(object):
    def __init__(self):
        self.s = set()
    def add_all(self, values):
        self.s.update(values)
    def remove_all(self, values):
        for value in values:
            self.s.discard(value)
    def get(self):
        return frozenset(self.s)
class ConfigList(object):
    def __init__(self):
        self.l = list()
    def add_all(self, values):
        self.l.extend(values)
    def remove_all(self, values):
        for value in values:
            try:
                self.l.remove(value)
            except ValueError:
                pass
    def get(self):
        return tuple(self.l)

class ConfigCollection(object):
    def __init__(self, key, t):
        self.key = key
        if t == 'list':
            self.constructor = ConfigList
        elif t == 'set':
            self.constructor = ConfigSet
        else:
            raise Exception('unknown collection type: ' + t + ' in ' + key)
        self.actions = []
    def add(self, value, priority):
        self.actions.append((lambda c: c.add_all(parse_values(value)), priority))
        self.actions.sort(key=lambda x:x[1])
    def remove(self, value, priority):
        self.actions.append((lambda c: c.remove_all(parse_values(value)), priority))
        self.actions.sort(key=lambda x:x[1])
    def get(self):
        collection = self.constructor()
        for (action, priority) in self.actions:
            action(collection)
        return collection.get()

class ConfigLoader(object):
    def __init__(self):
        self.config_actions = []

    def build(self):
        numbered_config_actions = list(enumerate(self.config_actions))
        config = Config()
        config.assign('system.distributor_id', execute_with_stdout(['lsb_release', '-is']).strip())
        config.assign('system.codename', execute_with_stdout(['lsb_release', '-cs']).strip())
        config.assign('system.processor', execute_with_stdout(['uname', '-p']).strip())
        evaluate_config(numbered_config_actions, config)
        return config

    def load_file(self, filename):
        self.config_actions.extend(parse_config_file(filename))


def evaluate_tag(config, tag):
    parts = re.split('\s*&&\s*', tag)
    result = True
    for part in parts:
        part_pieces = re.split('\s*==\s*', part, 1)
        if len(part_pieces) == 2:
            key = part_pieces[0]
            value = parse_value(part_pieces[1])
            result = result and config[key] == value
        else:
            result = result and part in config.tags
    return result


def evaluate_config(config_actions, config):
    remaining_actions = []
    for indexed_action in config_actions:
        (index, action) = indexed_action
        tag = action[0]
        key = action[1][0]
        operation = action[1][1]
        value = action[1][2]

        if tag is None or evaluate_tag(config, tag):
            if operation == '=':
                config.assign(key, value, index)
            elif operation == '+=':
                config.add(key, value, index)
            elif operation == '-=':
                config.remove(key, value, index)
            elif operation == ':=':
                config.define(key, value)
            else:
                raise Exception('Unknown operation: '+s)
        else:
            remaining_actions.append(indexed_action)

    # recursivly apply actions until no more actions are applied
    if len(remaining_actions) > 0 and len(remaining_actions) != len(config_actions):
        evaluate_config(remaining_actions, config)

