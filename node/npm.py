from __future__ import absolute_import
import os
from build_util import *
from install_util import *
from module_base import *
from src_package import *
import logger
import subprocess

class InstallNpm(ModuleBase):
    def do_config(self):
        self.config.bash.add('path', ['~/local/bin'], 0)

    @after('InstallNode')
    def do_install(self):
        if self.config.install and self.config.node.install:
            package = SrcPackage('npm', GitRepo('https://github.com/npm/npm.git', 'v1.4.21'), self)
            package.update()
            package.configure('~/local')
            package.make_install()


class NpmInstall(ModuleBase):
    @after('InstallNpm')
    def do_install(self):
        if self.config.install:
            for package in self.config.node.npm.install:
                with logger.trylog('Running npm install '+package):
                    subprocess.call(['npm', 'install', '-g', package])

