from __future__ import absolute_import
from dotfiles.package_base import *
from dotfiles.actions import *
import os

@suggests('rosdep')
@suggests('robot_aliases')
@suggests('rossetup')
@suggests('apt-get:python-catkin-lint')
@suggests('apt-get:python-rosinstall')
@suggests('apt-get:python-wstool')
class ros(PackageBase):
    def setup_sources(self):
        logger.log('Installing ROS '+self.config.ros.version)
        ros_package_repo = 'deb http://packages.ros.org/ros/ubuntu '+self.config.system.codename+' main'
        ros_repo_file = '/etc/apt/sources.list.d/ros-latest.list'
        if not (os.path.isfile(ros_repo_file) and ros_package_repo in open(ros_repo_file, 'r').read()):
            with logger.trylog('Installing ROS repo source and key'):
                logger.call('sudo sh -c \'echo "'+ros_package_repo+'" > '+ros_repo_file+'\'', shell=True)
                logger.call('wget https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -O - | sudo apt-key add -', shell=True)

    def install(self):
        apt_get_packages = []
        apt_get_packages.append('ros-'+self.config.ros.version+'-desktop-full')
        apt_get_packages.extend(['ros-'+self.config.ros.version+'-'+package.replace('_', '-') for package in self.config.ros.packages.install])
        return concat_lists(
            [self.setup_sources],
            self.action('apt-get').update(),
            self.action('apt-get').install(apt_get_packages)
        )


@depends('ros')
class rosdep(PackageBase):
    def install(self):
        actions = []
        if not os.path.isfile('/etc/ros/rosdep/sources.list.d/20-default.list'):
            actions.append(CommandAction(['sudo', 'rosdep', 'init']))
        actions.append(CommandAction(['rosdep', 'update']))
        return actions
