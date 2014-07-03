#!/usr/bin/python
import os
import shutil
import imp
import sys
import glob
import subprocess
import argparse


BUILD_UTIL_DIR_NAME = 'build_util'
rootdir = os.path.dirname(os.path.realpath(__file__))
buildutildir = os.path.join(rootdir, BUILD_UTIL_DIR_NAME)
sys.path.append(buildutildir)

from config_util import load_configs
import module_base



BUILD_DIR_NAME = 'build'
GIT_DIR_NAME = '.git'

bash_normal = '\033[0m'
bash_red = '\033[0;31m'
bash_green = '\033[0;32m'
bash_yellow = '\033[0;33m'

def load_py(name, path):
    return imp.load_source(name, path)


class FileModule(module_base.ModuleBase):
    def __init__(self, context, filepath):
        module_base.ModuleBase.__init__(self, context)
        self.filepath = filepath
        
    def do_config(self):
        self.get_file_processor(self.filepath).do_config(self.filepath, self.context)

    def do_build(self):
        self.get_file_processor(self.filepath).do_build(self.filepath, self.context)

    def do_install(self):
        self.get_file_processor(self.filepath).do_install(self.filepath, self.context)


def process_folder(name, path, builddir, config):
    print '\t', name
    folder_builddir = builddir
    common = module_base.ModuleCommon()

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

        context = module_base.ModuleContext(os.path.dirname(filename), folder_builddir, config, common)
        if filename.endswith('.py'):
            try:
                py_mod = load_py(name+'.'+filename.replace('.py', ''), filepath)
                mod_found = False
                for name in py_mod.__dict__:
                    if name == 'ModuleBase':
                        continue
                    thing = py_mod.__dict__[name]
                    #TODO figure out how to do class type instead of this
                    if isinstance(thing, type(module_base.ModuleBase)) and issubclass(thing, module_base.ModuleBase):
                        print bash_green+'\t\tUsing module: '+filename+':'+name+bash_normal
                        mod_found = True
                        config_mods.append(thing(context))
                if not mod_found:
                    print bash_red+'\t\tNo modules found in: '+filename+bash_normal
            except IOError as e:
                print 'Error loading module', e
        else:
            pass
            print bash_green+'\t\tUsing File: '+filename+bash_normal
            config_mods.append(FileModule(context, filepath))
            
    for mod in config_mods:
        mod.do_init()
    for mod in config_mods:
        mod.do_config()
    for mod in config_mods:
        mod.do_build()
    for mod in config_mods:
        mod.do_install()


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
    print 'Root Dir: ', rootdir

    config = load_configs([os.path.join(rootdir, 'base.conf'), os.path.expanduser('~/.dotfiles.conf')])

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
            install_command.extend(['ros-'+config.ros.version+'-'+package.replace('_', '-') for package in config.ros.packages.install])
            install_command.append('python-catkin-lint')
            install_command.append('python-rosinstall')
            install_command.append('python-wstool')
            

        if args.update:
            subprocess.call(['sudo', 'apt-get', '-y', 'update'])
        subprocess.call(install_command)

        if config.ros.install and args.update:
            if subprocess.call('rosdep update 2>/dev/null', shell=True) != 0:
                subprocess.call(['sudo', 'rosdep', 'init'])
                subprocess.call(['rosdep', 'update'])
            

if __name__ == "__main__":
    main()



