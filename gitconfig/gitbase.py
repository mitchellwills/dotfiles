from __future__ import absolute_import
import os
from collections import OrderedDict
from module_base import *


class GitConfigEntry:
    def __init__(self, value, comment):
        self.value = value
        self.comment = comment

class GitConfig(ModuleBase):
    def do_init(self):
        self.config.ensure('git.config')
        self.config.ensure('git.aliases')

    def add_config(self, name, value, comment = None):
        self.config.git.config[name] = value
        if comment is not None:
            self.config.git.config[name+'.comment'] = comment

    def do_config(self):
        for name in sorted(self.config.git.aliases.keys()):
            value = self.config.git.aliases[name]
            comment = self.config.git.aliases[name+'.comment']
            self.add_config('alias.'+name, value, comment)


    def do_build(self):
        with open(self.build_file('.gitconfig'), 'w') as f:
            for category in self.config.git.config.keys():
                f.write('['+category+']\n')
                for key in self.config.git.config[category].keys():
                    value = self.config.git.config[category][key]
                    comment = self.config.git.config[category][key+'.comment']
                    if comment is not None:
                        f.write('\t# '+comment+'\n')
                    f.write('\t'+key+' = '+self.eval_templates(value)+'\n')
                f.write('\n')

    def do_install(self):
        self.symlink(self.home_file('.gitconfig'), self.build_file('.gitconfig'))
