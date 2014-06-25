#!/usr/bin/python
import os
import shutil
import imp
import sys
import glob
import subprocess
import argparse

BUILD_UTIL_DIR_NAME = 'build_util'

BUILD_DIR_NAME = 'build'
GIT_DIR_NAME = '.git'

def load_module(name, path):
    return imp.load_source(name, path)


class ModuleConfigurationProxy:
    def __init__(self, module):
        self.module = module
    def init(self, data):
        if hasattr(self.module, 'init'):
            return self.module.init(data)
    def config(self, data, config):
        if hasattr(self.module, 'config'):
            return self.module.config(data, config)
    def build(self, data, builddir):
        if hasattr(self.module, 'build'):
            return self.module.build(data, builddir)
    def install(self, data, builddir):
        if hasattr(self.module, 'install'):
            return self.module.install(data, builddir)

class FileConfigurationProxy:
    def __init__(self, filepath):
        self.filepath = filepath
    def init(self, data):
        if hasattr(data, '__init_file__'):
            return data.__init_file__(data, self.filepath)
    def config(self, data, config):
        if hasattr(data, '__config_file__'):
            return data.__config_file__(data, config, self.filepath)
    def build(self, data, builddir):
        if hasattr(data, '__build_file__'):
            return data.__build_file__(data, builddir, self.filepath)
    def install(self, data, builddir):
        if hasattr(data, '__install_file__'):
            return data.__install_file__(data, builddir, self.filepath)

class FolderData: pass
def process_folder(name, path, builddir, config):
    print '\t', name
    folder_builddir = builddir
    data = FolderData()

    config_mods = []
    files = [os.path.join(root, filename)
             for root, dirnames, filenames in os.walk(path)
             for filename in filenames]

    for filename in sorted(files):
        filepath = os.path.join(path, filename)
        if filename.endswith('~'):
            continue
        if filename.endswith('.pyc'):
            continue
        if not os.path.isfile(filepath):
            continue

        print '\t\tUsing: '+filename
        if filename.endswith('.py'):
            try:
                config_mod = ModuleConfigurationProxy(load_module(name+'.'+filename.replace('.py', ''), filepath))
                config_mods.append(config_mod)
            except IOError as e:
                print 'Error loading module', e
        else:
            config_mod = FileConfigurationProxy(filepath)
            config_mods.append(config_mod)
            
    for mod in config_mods:
        mod.init(data)
    for mod in config_mods:
        mod.config(data, config)
    for mod in config_mods:
        mod.build(data, folder_builddir)
    for mod in config_mods:
        mod.install(data, folder_builddir)


def prompt_yes_no(question):
    yes_responses = set(['y', 'yes'])
    no_responses = set(['n', 'no'])
    response = None
    while response not in yes_responses and response not in no_responses:
        response = raw_input(question + ' (y/N): ').lower()
    return response in yes_responses




def main():
    parser = argparse.ArgumentParser(description='Install dotfiles')
    parser.add_argument('--no-update', help="don't run apt-get update", dest='update', action='store_false', default=True)
    parser.add_argument('--no-install', help="don't run apt-get install", dest='install', action='store_false', default=None)
    parser.add_argument('--install', help="run apt-get install", dest='install', action='store_true', default=None)

    args = parser.parse_args()
    print args

    if args.install is None:
        args.install = prompt_yes_no('install software?')

    print 'building dotfiles'
    rootdir = os.path.dirname(os.path.realpath(__file__))
    print 'Root Dir: ', rootdir

    buildutildir = os.path.join(rootdir, BUILD_UTIL_DIR_NAME)
    sys.path.append(buildutildir)

    config = __import__('config_util').load_configs([os.path.join(rootdir, 'base.conf'), os.path.expanduser('~/.dotfiles.conf')])

    builddir = os.path.join(rootdir, BUILD_DIR_NAME)

    if os.path.exists(builddir):
        shutil.rmtree(builddir)
    os.mkdir(builddir)
    
    for filename in os.listdir(rootdir):
        fullpath = os.path.join(rootdir, filename)
        if os.path.isdir(fullpath) and filename != BUILD_DIR_NAME and filename != BUILD_UTIL_DIR_NAME and not filename.startswith('.') and not filename == 'tools':
            process_folder(filename, fullpath, builddir, config)

    if args.install:
        install_command = ['sudo', 'apt-get', '-y', 'install']
        install_command.extend(config.apt_get.install)

        if config.ros.install:
            print 'Installing ROS '+config.ros.version
            # setup ros package repo
            ros_package_repo = 'deb http://packages.ros.org/ros/ubuntu '+config.system.codename+' main'
            ros_repo_file = '/etc/apt/sources.list.d/ros-latest.list'
            if not (os.path.isfile(ros_repo_file) and ros_package_repo in open(ros_repo_file, 'r').read()):
                print 'Installing ROS repo source and key'
                subprocess.call('sudo sh -c \'echo "'+ros_package_repo+'" > '+ros_repo_file+'\'', shell=True)
                subprocess.call('wget https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -O - | sudo apt-key add -', shell=True)
                args.update = True # force update
            else:
                print 'ROS repo already installed'

            install_command.append('ros-'+config.ros.version+'-desktop-full')
            install_command.append('python-catkin-lint')
            install_command.append('python-rosinstall')
            

        if args.update:
            subprocess.call(['sudo', 'apt-get', '-y', 'update'])
        subprocess.call(install_command)

        if config.ros.install:
            if subprocess.call('rosdep update 2>/dev/null', shell=True) != 0:
                subprocess.call(['sudo', 'rosdep', 'init'])
                subprocess.call(['rosdep', 'update'])
            

if __name__ == "__main__":
    main()



