from __future__ import absolute_import
import os
import sys
import glob
import imp
import subprocess
import inspect
import importlib
import dotfiles.logger as logger


def suggests(spec):
    def wrap(func):
        if not hasattr(func, 'suggests'):
            func.suggests = set()
        func.suggests.add(spec)
        return func
    return wrap

def abstract(func):
    func.abstract = True
    return func

def depends(spec):
    def wrap(func):
        if not hasattr(func, 'deps'):
            func.deps = set()
        func.deps.add(spec)
        return func
    return wrap

def configures(spec):
    def wrap(func):
        if not hasattr(func, 'configures'):
            func.configures = set()
        func.configures.add(spec)
        return func
    return wrap


def read_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def concat_files(pathspec):
    files = glob.glob(pathspec)

    contents = ''
    for filepath in files:
        with open(filepath, 'r') as f:
            contents = contents + f.read()
    return contents

def all_files_recursive(path):
    return [os.path.join(root, filename)
            for root, dirnames, filenames in os.walk(path)
            for filename in filenames]

def load_py(name, path):
    for path_entry in sys.path:
        if path.startswith(path_entry):
            module_name = os.path.relpath(path, path_entry).replace('.py', '').replace('/', '.')
            try:
                module = importlib.import_module(module_name)
                logger.log('Loaded module from path: '+module_name, verbose=True)
                return module
            except ImportError:
                pass # not in module
    return imp.load_source(name, path)


def prompt_yes_no(question):
    yes_responses = set(['y', 'yes'])
    no_responses = set(['n', 'no'])
    response = None
    while response not in yes_responses and response not in no_responses:
        response = raw_input(question + ' (y/N): ').lower()
    return response in yes_responses

def execute_with_stdout(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out

def names_of_items(l):
    return map(lambda item: item.name(), l)

def find_by_name(l, name):
    for item in l:
        if item.name() == name:
            return item
    return None

def object_deps(obj):
    if hasattr(obj.__class__, 'deps'):
        return obj.__class__.deps
    return set()

def object_suggestions(obj):
    if hasattr(obj.__class__, 'suggests'):
        return obj.__class__.suggests
    return set()

def object_configures(obj):
    if hasattr(obj.__class__, 'configures'):
        return obj.__class__.configures
    return set()

def is_abstract(obj):
    if inspect.isclass(obj):
        clazz = obj
    else:
        clazz = obj.__class__
    if 'abstract' in clazz.__dict__:
        return clazz.abstract
    return False

def concat_lists(*args):
    result = []
    for l in args:
        result.extend(l)
    return result
