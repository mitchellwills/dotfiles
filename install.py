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
    

def main():
    parser = argparse.ArgumentParser(description='Install dotfiles')
    parser.add_argument('--no-update', help="don't run apt-get update", action='store_true')
    parser.add_argument('--no-install', help="don't run apt-get install", action='store_true')

    args = parser.parse_args()
    print args

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

    if not args.no_update:
        subprocess.call(['sudo', 'apt-get', '-y', 'update'])
    if not args.no_install:
        install_command = ['sudo', 'apt-get', '-y', 'install']
        install_command.extend(config.apt_get.install)
        subprocess.call(install_command)

if __name__ == "__main__":
    main()



