from __future__ import absolute_import
import os
from build_util import *
from install_util import *
from module_base import *

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
    #TODO actually escape string
    return "'"+value+"'"
    




class Bashrc(ModuleBase):
    def do_init(self):
        commands = []
        self.def_common('commands', commands)
        self.def_common('add_command', lambda command: commands.append(command))
        self.def_common('code', lambda code: self.add_command(BashCode(code)))

        self.def_common('setopt', lambda opt: self.code('shopt -s '+opt))
        self.def_common('assign', lambda name, value: self.code(name+'='+value))

        self.def_common('alias', lambda name, value, comment = None: self.add_command(BashAlias(name, quote_and_escape(value), comment)))
        self.def_common('alias_raw', lambda name, value, comment = None: self.add_command(BashAlias(name, value, comment)))

        self.def_common('comment', lambda comment: self.add_command(BashComment(comment)))
        self.def_common('_', lambda: self.add_command(BashEmptyLine()))

        self.def_file_processor_for_regex_match('.*/.*\.bash', CustomFileProcessor(config=lambda filepath, context: self.do_config_file(filepath, context)))

    def do_config_file(self, filepath, context):
        self.add_command(BashFileContents(filepath))

    def do_build(self):
        with open(self.build_file('.bashrc'), 'a') as f:
            for command in self.commands:
                f.write(command.build()+'\n')

    def do_install(self):
        install_symlink_in_home('.bashrc', self.build_file('.bashrc'))
