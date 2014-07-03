from __future__ import absolute_import
import os
import shutil
from install_util import *
from module_base import *

class Colors(ModuleBase):
    def do_init(self):
        self.def_file_processor_for_file('LS_COLORS', HomeSymlinkFileProcessor('.dircolors'))
