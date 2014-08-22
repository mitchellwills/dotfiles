from __future__ import absolute_import
import os
from dotfiles.package_base import *
from dotfiles.util import *
import dotfiles.logger as logger
import glob

class EmacsMoveBorder(PackageBase):
    def name(self):
        return 'emacs-move-border'
    def install(self):
        return concat_lists(
            self.action('net').download(self.build_file('move-border.el'), 'https://raw.githubusercontent.com/ramnes/move-border/master/move-border.el'),
            self.action('file').mkdir(self.home_file('.emacs.d')),
            self.action('file').symlink(self.home_file('.emacs.d/move-border.el'), self.build_file('move-border.el'))
        )

@depends('emacs-move-border')
class EmacsConf(PackageBase):
    def name(self):
        return 'emacs-conf'

    def install(self):
        return self.action('file').symlink(self.home_file('.emacs'), self.base_file('emacs/base.emacs'))
