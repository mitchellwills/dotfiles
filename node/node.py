from __future__ import absolute_import
import os
from build_util import *
from install_util import *
from module_base import *
from src_package import *
import logger
import subprocess

class InstallNode(ModuleBase):
    def do_config(self):
        self.config.bash.add('path', ['~/local/bin'], 0)

    @after('AptGetInstall')
    def do_install(self):
        if self.config.install and self.config.node.install:
            package = SrcPackage('node', GitRepo('https://github.com/joyent/node.git', 'v0.11.13'), self)
            package.update()
            package.configure('~/local')
            package.make_install()
