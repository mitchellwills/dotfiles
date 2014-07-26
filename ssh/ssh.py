from __future__ import absolute_import
import os
from collections import OrderedDict
from install_util import *
from module_base import *

class HostConfig(object):
    def __init__(self, host, user, hostname, identity):
        self.host = host
        self.user = user
        self.hostname = hostname
        self.identity = identity

class SshConfig(ModuleBase):
    def parse_ssh_host(self, label, data):
        if type(data) is str:
            full_match = re.match('(?:(.+?)\s*>\s*)?(?:(.+?)@)?(.+)', data)
            if full_match:
                host = full_match.group(1)
                if host is None:
                    host = label
                return HostConfig(host, full_match.group(2), full_match.group(3), None)
            else:
                raise Exception('Unknown ssh host format: '+data)
        else:
            return data

    def do_build(self):
        with open(self.build_file('.ssh_config'), 'w') as f:
            for identity in self.config.ssh.identities:
                f.write('IdentityFile '+identity+'\n\n')
            if self.config.ssh.hosts is not None:
                for hostlabel in self.config.ssh.hosts.keys():
                    host_conf = self.parse_ssh_host(hostlabel, self.config.ssh.hosts[hostlabel])
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
