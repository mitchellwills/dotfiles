from __future__ import absolute_import
import os
import shutil
from install_util import *
from module_base import *

class Colors(ModuleBase):
    def do_install(self):
        install_symlink_in_home('.dircolors', self.module_file('LS_COLORS'))
