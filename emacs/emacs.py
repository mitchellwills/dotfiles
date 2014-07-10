from __future__ import absolute_import
import os
from build_util import *
from install_util import *
from module_base import *
import logger

class Emacs(ModuleBase):
    def do_init(self):
        self.def_file_processor_for_regex_match('.+/.*\.emacs', AmendBuildFileProcessor('.emacs'))


    def do_build(self):
        self.download_build_file('move-border.el', 'https://raw.githubusercontent.com/ramnes/move-border/master/move-border.el')

    def do_install(self):
        if not os.path.isdir(self.home_file('.emacs.d')):
            with logger.trylog('creating .emacs.d folder'):
                os.mkdir(self.home_file('.emacs.d'))
        install_symlink_in_home('.emacs.d/move-border.el', self.build_file('move-border.el'))
        install_symlink_in_home('.emacs', self.build_file('.emacs'))
