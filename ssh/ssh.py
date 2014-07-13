from __future__ import absolute_import
import os
from collections import OrderedDict
from install_util import *
from module_base import *

class SshConfig(ModuleBase):
    def do_build(self):
        with open(self.build_file('.ssh_config'), 'w') as f:
            for identity in self.config.ssh.identities:
                f.write('IdentityFile '+identity+'\n\n')
            if self.config.ssh.hosts is not None:
                for hostlabel in self.config.ssh.hosts.keys():
                    host_conf = self.config.ssh.hosts[hostlabel]
                    f.write('Host '+host_conf.host+'\n')
                    if host_conf.identity is not None:
                        f.write('\tIdentityFile '+host_conf.identity+'\n')
                    if host_conf.user is not None:
                        f.write('\tUser '+host_conf.user+'\n')
                    if host_conf.hostname is not None:
                        f.write('\tHostName '+host_conf.hostname+'\n')
                    f.write('\n')

    def do_install(self):
        install_symlink_in_home('.ssh/config', self.build_file('.ssh_config'))
