from __future__ import absolute_import
from dotfiles.module_base import *

class Colors(ModuleBase):
    def do_install(self):
        self.symlink(self.home_file('.dircolors'), self.module_file('LS_COLORS'))
