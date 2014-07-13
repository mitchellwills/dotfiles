from __future__ import absolute_import
import os
from collections import OrderedDict
from install_util import *
from module_base import *


class GitConfigEntry:
    def __init__(self, value, comment):
        self.value = value
        self.comment = comment

class GitConfig(ModuleBase):
    def do_init(self):
        self.config.ensure('git.config')
        def add_config(name, value, comment = None):
            self.config.git.config[name] = value
            if comment is not None:
                self.config.git.config[name+'.comment'] = comment

        self.def_common('add_config', add_config)

    def do_config(self):
        self.add_config('user.name', self.config.identity.name)
        self.add_config('user.email', self.config.identity.email)

        self.add_config('color.branch', 'auto')
        self.add_config('color.diff', 'auto')
        self.add_config('color.interactive', 'auto')
        self.add_config('color.status', 'auto')

        self.add_config('push.default', 'simple')

    def do_build(self):
        with open(self.build_file('.gitconfig'), 'w') as f:
            for category in self.config.git.config.keys():
                f.write('['+category+']\n')
                for key in self.config.git.config[category].keys():
                    value = self.config.git.config[category][key]
                    comment = self.config.git.config[category][key+'.comment']
                    if comment is not None:
                        f.write('\t# '+comment+'\n')
                    f.write('\t'+key+' = '+value+'\n')
                f.write('\n')

    def do_install(self):
        install_symlink_in_home('.gitconfig', self.build_file('.gitconfig'))
