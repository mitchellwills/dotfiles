from __future__ import absolute_import
import os
import shutil
from build_util import *
from module_base import *


class Robots(ModuleBase):
    def do_config(self):
        self.config.ensure('robots')
        for robot in self.config.robots.keys():
            robot_config = self.config.robots[robot]
            robot_ssh_host_config = self.config.ensure('ssh.hosts.'+robot)
            robot_ssh_host_config.assign('host', robot)
            robot_ssh_host_config.assign('user', robot_config.user)
            robot_ssh_host_config.assign('hostname', robot_config.host)

