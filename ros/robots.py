from __future__ import absolute_import
from dotfiles.package_base import *

@configures('ssh_config')
class robot_aliases(PackageBase):
    def configure_ssh_hosts(self):
        self.config.ensure('robots')
        for robot in self.config.robots.keys():
            robot_config = self.config.robots[robot]
            robot_ssh_host_config = self.config.ensure('ssh.hosts.'+robot)
            robot_ssh_host_config.assign('host', robot)
            robot_ssh_host_config.assign('user', robot_config.user)
            robot_ssh_host_config.assign('hostname', robot_config.host)

    def install(self):
        return [self.configure_ssh_hosts]
