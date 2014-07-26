from __future__ import absolute_import
from dotfiles.module_base import *
from dotfiles.src_package import *

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
