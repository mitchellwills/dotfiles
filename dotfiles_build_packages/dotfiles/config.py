from __future__ import absolute_import
import os
import re
import dotfiles.logger as logger
from dotfiles.util import *

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
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_store', store)
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
    def __setattr__(self, name, value):
        raise Exception('Cannot set attribute directly, you must use a modifier function instead')
    def __setitem__(self, name, value):
        self.assign(name, value, None)
    def __getitem__(self, name):
        return self.__getattr__(name)
    def __contains__(self, name):
        return name in self.keys()
    def keys(self):
        subkeys = map(lambda key: key.replace(self._prefix, ''), filter(lambda k: k.startswith(self._prefix), self._store))
        subkeys = set(map(lambda key: key.split('.', 1)[0], subkeys))
        subkeys.discard('')
        return subkeys
    def ensure(self, name):
        self.assign(name+'.', 'ENSURE')
        return self[name]
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


class ConfTag(object):
    def __init__(self, tag):
        self.tag = tag
class ConfPrefix(object):
    def __init__(self, prefix):
        self.prefix = prefix
class ConfStack(object):
    def __init__(self):
        self.stack = []
    def push(self, item, depth):
        self.stack.append(item)
    def pop_to_depth(self, depth):
        while self.size() > depth:
            self.stack.pop()
    def size(self):
        return len(self.stack)

    def tag(self):
        tags = map(lambda tag: tag.tag, filter(lambda x: type(x) is ConfTag, self.stack))
        if len(tags) > 0:
            return ' && '.join(tags)
        return None
    def prefix(self, key):
        prefixes = map(lambda prefix: prefix.prefix, filter(lambda x: type(x) is ConfPrefix, self.stack))
        if len(prefixes) > 0:
            return '.'.join(prefixes)+'.'+key
        return key

def parse_config_file(filename):
    config_actions = []
    stack = ConfStack()
    previous_line_comment = None
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            for line in f:
                if re.search('^ +', line) is not None:
                    raise Exception('line starts with non tab: "'+line+'"')
                m = re.search('^(\t*)(\s*)(.+)', line)
                if m is not None:
                    depth = len(m.group(1))
                    if len(m.group(2)) > 0:
                        raise Exception('Found spaces at the beginning of a line: "'+line+'"')

                    line_contents = m.group(3).rstrip()
                    if line_contents.startswith('#'):
                        continue # skip comment

                    if depth <= stack.size():
                        stack.pop_to_depth(depth)
                        tag_match = re.match('\[([^\]]+)\]', line_contents)
                        parts = re.split('\s*([\+:-]?=)\s*', line_contents, 1)
                        if tag_match is not None:
                            if previous_line_comment is not None:
                                raise Exception('Cannot have conf comment on tag')
                            tag = tag_match.group(1)
                            stack.push(ConfTag(tag), depth)
                        elif line_contents.startswith(':'):
                            stack.push(ConfPrefix(line_contents[1:]), depth)
                            if previous_line_comment is not None:
                                config_actions.append((stack.tag(), (stack.prefix('comment'), '=', previous_line_comment)))
                                previous_line_comment = None
                        elif len(parts) == 3:
                            key = parts[0]
                            operation = parts[1]
                            value = parts[2]
                            config_actions.append((stack.tag(), (stack.prefix(key), operation, value)))
                            if previous_line_comment is not None:
                                config_actions.append((stack.tag(), (stack.prefix(key+'.comment'), '=', previous_line_comment)))
                                previous_line_comment = None
                        elif line_contents.startswith('%'):
                            if previous_line_comment is not None:
                                raise Exception('Can only have one line conf comment')
                            previous_line_comment = line_contents[1:].lstrip()
                        else:
                            raise Exception('Unknown command: "'+line_contents+'"')
                    else:
                        raise Exception('Expected indent of '+str(stack.size())+' or less on line: "'+line+'"')
                else:
                    pass # skip blank line
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

