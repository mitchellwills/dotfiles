from __future__ import absolute_import
import os
from build_util import *
from module_base import *
import logger
import glob

class Emacs(ModuleBase):
    def do_build(self):
        self.download_build_file('move-border.el', 'https://raw.githubusercontent.com/ramnes/move-border/master/move-border.el')
        self.concatenate_files_to_build(glob.glob(self.module_file('*.emacs')), '.emacs')

    def do_install(self):
        if not os.path.isdir(self.home_file('.emacs.d')):
            with logger.trylog('creating .emacs.d folder'):
                os.mkdir(self.home_file('.emacs.d'))
        self.symlink(self.home_file('.emacs.d/move-border.el'), self.build_file('move-border.el'))
        self.symlink(self.home_file('.emacs'), self.build_file('.emacs'))
