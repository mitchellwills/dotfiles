from __future__ import absolute_import
from dotfiles.module_base import *
import os

class RosPackage(ModuleBase):
    def do_config(self):
        self.config.apt_get.add('install', ['ros-'+self.config.ros.version+'-desktop-full'], 0)
        self.config.apt_get.add('install', ['ros-'+self.config.ros.version+'-'+package.replace('_', '-') for package in self.config.ros.packages.install], 0)

class RosRepo(ModuleBase):
    def do_config(self):
        self.ros_package_repo = 'deb http://packages.ros.org/ros/ubuntu '+self.config.system.codename+' main'
        self.ros_repo_file = '/etc/apt/sources.list.d/ros-latest.list'
        if self.config.install and self.config.ros.install:
            if not (os.path.isfile(self.ros_repo_file) and self.ros_package_repo in open(self.ros_repo_file, 'r').read()):
                self.config.ros.assign('update_repo', True)
                self.config.assign('update', True)
            else:
                logger.warning('ROS repo already installed')
        else:
            logger.warning('Not checking ROS apt-get repo status')


    @before('AptGetUpdate')
    def do_install(self):
        if self.config.install and self.config.ros.install:
            logger.log('Installing ROS '+self.config.ros.version)
            # setup ros package repo
            if self.config.ros.update_repo:
                with logger/etc/ros/rosdep/sources.list.d/20-defaul.trylog('Installing ROS repo source and key'):
                    logger.call('sudo sh -c \'echo "'+self.ros_package_repo+'" > '+self.ros_repo_file+'\'', shell=True)
                    logger.call('wget https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -O - | sudo apt-key add -', shell=True)
        else:
            logger.warning('Not installing ROS apt-get repo')

class RosDep(ModuleBase):
    @after('AptGetInstall')
    def do_install(self):
        if self.config.install and self.config.ros.install:
            if not os.path.isfile('/etc/ros/rosdep/sources.list.d/20-default.list'):
                logger.call(['sudo', 'rosdep', 'init'])
            else:
                logger.warning('rosdep already initialized')

            if self.config.update:
                logger.call(['rosdep', 'update'])
            else:
                logger.warning('Not updating rosdep')
        else:
            logger.warning('Not installing')
