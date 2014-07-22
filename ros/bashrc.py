from __future__ import absolute_import
import os
import shutil
from build_util import *
from install_util import *
from module_base import *


class Rossetup(ModuleBase):
    @before('Bashrc')
    def do_build(self):
        if self.config.ros.install:
            open(self.build_file('gen/95-ros.bash'), 'w').write('source ~/.rossetup\n')
            self.eval_file_templates_to_build(self.module_file('.rossetup'), '.rossetup')

    def do_install(self):
        if self.config.ros.install:
            install_symlink_in_home('.rossetup', self.build_file('.rossetup'))

