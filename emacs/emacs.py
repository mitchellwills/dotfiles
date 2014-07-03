from __future__ import absolute_import
import os
from build_util import *
from install_util import *
from module_base import *

class Emacs(ModuleBase):
    def do_init(self):
        self.def_file_processor_for_regex_match('.+/.*\.emacs', AmendBuildFileProcessor('.emacs'))


    def do_install(self):
        install_symlink_in_home('.emacs', self.build_file('.emacs'))
