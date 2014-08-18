import os
import glob
import imp
import subprocess
import inspect


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

def is_abstract(obj):
    if inspect.isclass(obj):
        clazz = obj
    else:
        clazz = obj.__class__
    if hasattr(clazz, 'abstract'):
        return clazz.abstract
    return False

def concat_lists(*args):
    result = []
    for l in args:
        result.extend(l)
    return result
