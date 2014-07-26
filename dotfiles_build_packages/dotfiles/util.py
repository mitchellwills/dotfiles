import os
import glob
import imp

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

