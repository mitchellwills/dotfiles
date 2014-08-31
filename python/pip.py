from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.src_package import *
from dotfiles.util import *
from dotfiles.actions import *
import dotfiles.logger as logger
import subprocess


class PipActionFactory(PackageActionFactory):
    def name(self):
        return 'pip'

    def install(self, packages):
        command = ['pip', 'install']
        if self.config.local:
            command.append('--install-option=--prefix='+os.path.expanduser(self.config.local_install.dir))
        else:
            command.insert(0, 'sudo')
        command.extend(packages)
        return [CommandAction(command, deps=['pip'])]


class pip(PackageBase):
    def already_installed(self):
        try:
            return subprocess.call(['pip', '-V']) == 0
        except OSError:
            return False
    def install(self):
        if self.config.local:
            if self.already_installed():
                logger.log('Installing local, but detected pip already installed', verbose = True)
                return []
            else:
                return concat_lists(
                    self.action('net').wget(self.build_file('get-pip.py'), 'https://bootstrap.pypa.io/get-pip.py'),
                    [CommandAction(['python'+self.config.python.version, 'get-pip.py', '--user'], cwd=self.build_file(''))]
                    )
        else:
            return self.action('apt-get').install(['python-pip'])

@abstract
@depends('pip')
class PipPackage(PackageBase):
    def __init__(self, package):
        self.package = package

    def name(self):
        return 'pip:'+self.package

    def install(self):
        return self.action('pip').install([self.package])

class PipPackageFactory(PackageFactory):
    def name(self):
        return 'pip'

    def build(self, name):
        return PipPackage(name)
