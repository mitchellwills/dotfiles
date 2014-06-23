from __future__ import absolute_import
import os
from build_util import *
from install_util import *

class BashFileContents():
    def __init__(self, filepath):
        self.filepath = filepath
    def build(self):
        return open(self.filepath, 'r').read()

class BashCode():
    def __init__(self, code):
        self.code = code
    def build(self):
        return self.code

class BashComment():
    def __init__(self, comment):
        self.comment = comment
    def build(self):
        return '# '+self.comment
class BashEmptyLine():
    def build(self):
        return ''

class BashAlias():
    def __init__(self, name, value, comment = None):
        self.name = name
        self.value = value
        self.comment = comment
    def build(self):
        if self.comment is not None:
            return 'alias '+self.name+'='+self.value+' # '+self.comment
        else:
            return 'alias '+self.name+'='+self.value

def quote_and_escape(value):
    return "'"+value+"'"
    

def config_file(obj, filepath):
    if filepath.endswith('.bash'):
        obj.add_command(BashFileContents(filepath))

def init(obj):
    obj.commands = []
    obj.add_command = lambda command: obj.commands.append(command)
    obj.code = lambda code: obj.add_command(BashCode(code))

    obj.setopt = lambda opt: obj.code('shopt -s '+opt)
    obj.assign = lambda name, value: obj.code(name+'='+value)

    obj.alias = lambda name, value, comment = None: obj.add_command(BashAlias(name, quote_and_escape(value), comment))
    obj.alias_raw = lambda name, value, comment = None: obj.add_command(BashAlias(name, value, comment))

    obj.comment = lambda comment: obj.add_command(BashComment(comment))
    obj._ = lambda: obj.add_command(BashEmptyLine())

    obj.__config_file__ = lambda obj, config, filepath: config_file(obj, filepath)


def config(obj, config):
    pass

def build(obj, builddir):
    with open(os.path.join(builddir, '.bashrc'), 'w') as f:
        f.write(open(os.path.join(builddir, '.bashrc'), 'r').read())
        for command in obj.commands:
            f.write(command.build()+'\n')

def install(obj, builddir):
    install_symlink_in_home('.bashrc', os.path.join(builddir, '.bashrc'))
