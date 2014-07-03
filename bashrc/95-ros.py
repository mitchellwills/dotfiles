from __future__ import absolute_import
import os
import shutil
from build_util import *
from install_util import *
from module_base import *


class Rossetup(ModuleBase):
    def do_init(self):
        if self.config.ros.install:
            self.def_file_processor_for_file('.rossetup', HomeSymlinkFileProcessor())

