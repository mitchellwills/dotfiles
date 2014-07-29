#!/usr/bin/python
import os
import shutil
import sys
import glob
import argparse
import inspect

from dotfiles.config import ConfigLoader
from dotfiles.util import *
import dotfiles.module_base as module_base
import dotfiles.package_base as package_base
import dotfiles.logger as logger


BUILD_DIR_NAME = 'build'
SRC_DIR_NAME = 'src'
GIT_DIR_NAME = '.git'
BUILD_UTIL_DIR_NAME = 'dotfiles_build_packages'

def value_or_empty_set(obj, name):
    if hasattr(obj, name):
        return getattr(obj, name)
    return set()

class Step():
    def __init__(self, mod, func):
        self.func = func
        self.mod = mod
        self.deps = set()
    def mod_name(self):
        return self.mod.__class__.__name__

def process_modules(config_mods, func_name):
    steps = dict()
    for mod in config_mods:
        if hasattr(mod, func_name):
            func = getattr(mod, func_name)
            step = Step(mod, func)
            step.deps.update(value_or_empty_set(func, 'after'))
            step.deps.update(value_or_empty_set(mod.__class__, 'after'))
            steps[step.mod_name()] = step

    # move items from before to the coresponding after
    for mod_name in steps:
        step = steps[mod_name]
        for build_dep in value_or_empty_set(func, 'before') | value_or_empty_set(mod, 'before'):
            if build_dep not in steps:
                raise Exception('No module found: ' + build_dep + ', was dep for ' + mod_name)
            else:
                dependancies[build_dep].deps.add(mod_name)

    # evaluate steps respecting dependancies
    evaluated = set()
    while True:
        evaluated_on_pass = set()
        for mod_name in steps:
            step = steps[mod_name]
            if evaluated.issuperset(step.deps):
                with logger.frame(mod_name+'.'+func_name+': '+str(list(step.deps))):
                    step.func()
                    evaluated_on_pass.add(mod_name)

        evaluated.update(evaluated_on_pass)
        for mod_name in evaluated_on_pass:
            steps.pop(mod_name)

        if len(steps) == 0:
            break
        if len(evaluated_on_pass) == 0:
            raise Exception('unresolvable dependancies for: ', dependancies.keys())

def process_folder(name, path, builddir, global_context, config_mods):
    folder_builddir = builddir
    common = module_base.ModuleCommon()

    files = all_files_recursive(path)

    for filename in files:
        filepath = os.path.join(path, filename)
        if filename.endswith('~'):
            continue
        if filename.endswith('.pyc'):
            continue
        if not os.path.isfile(filepath):
            continue

        context = module_base.ModuleContext(global_context, os.path.dirname(filename), folder_builddir, common)
        if filename.endswith('.py'):
            try:
                py_mod = load_py(name+'.'+filename.replace('.py', ''), filepath)
                mod_found = False
                for name in py_mod.__dict__:
                    thing = py_mod.__dict__[name]
                    if inspect.isclass(thing):
                        if thing.__module__ == 'dotfiles.package_base' or thing.__module__ == 'dotfiles.module_base':
                            continue
                        if issubclass(thing, module_base.ModuleBase):
                            logger.success('Loading module: '+filename+':'+name, verbose=True)
                            mod_found = True
                            config_mods.append(thing(context))
                if not mod_found:
                    logger.failed('No modules found in: '+filename)
            except IOError as e:
                logger.failed( 'Error loading module: '+str(e))



def main(rootdir):
    parser = argparse.ArgumentParser(description='Install dotfiles')
    parser.add_argument('--no-update', help="don't run apt-get update", dest='update', action='store_false', default=True)
    parser.add_argument('--no-install', help="don't run apt-get install", dest='install', action='store_false', default=None)
    parser.add_argument('--install', help="run apt-get install", dest='install', action='store_true', default=None)
    parser.add_argument('--upgrade', help="run apt-get upgrade", dest='upgrade', action='store_true', default=False)
    parser.add_argument('--verbose', help="print verbose output", dest='verbose', action='store_true', default=False)

    args = parser.parse_args()
    logger.init(args.verbose)

    if args.install is None:
        args.install = prompt_yes_no('install software?')

    logger.log('Root Dir: ' + rootdir)

    builddir = os.path.join(rootdir, BUILD_DIR_NAME)
    srcdir = os.path.join(rootdir, SRC_DIR_NAME)


    if os.path.exists(builddir):
        shutil.rmtree(builddir)
    os.mkdir(builddir)
    if not os.path.exists(builddir):
        os.mkdir(srcdir)

    with logger.frame('Loading Configuration'):
        config_loader = ConfigLoader()
        conf_files = filter(lambda f: f.endswith('.conf') and not f.startswith(srcdir), all_files_recursive(rootdir))
        for f in conf_files:
            with logger.trylog('loading conf: '+f):
                config_loader.load_file(f)
        with logger.trylog('loading user conf file'):
            config_loader.load_file(os.path.expanduser('~/.dotfiles.conf'))


        config = config_loader.build()
        config.assign('install', args.install, float("inf"))
        config.assign('update', args.update, float("inf"))
        config.assign('upgrade', args.upgrade, float("inf"))

        if config.sudo is None:
            config.assign('sudo', prompt_yes_no('use sudo'), float("inf"))

    global_context = module_base.GlobalContext(rootdir, srcdir, config)


    config_mods = []
    config_pkgs = []
    with logger.frame('Loading Modules'):
        for filename in os.listdir(rootdir):
            fullpath = os.path.join(rootdir, filename)
            if os.path.isdir(fullpath) and filename != BUILD_DIR_NAME and filename != BUILD_UTIL_DIR_NAME and not filename.startswith('.') and not filename == 'tools' and not filename == SRC_DIR_NAME:
                with logger.frame('Loading '+filename):
                    process_folder(filename, fullpath, builddir, global_context, config_mods)

    with logger.frame('do_init'):
        process_modules(config_mods, 'do_init')
    with logger.frame('do_config'):
        process_modules(config_mods, 'do_config')


    current_path = os.environ['PATH']
    path = ''
    if len(current_path) > 0:
        path = ':'+current_path
    path = ':'.join([os.path.expanduser(element) for element in config.bash.path]) + path
    os.environ['PATH'] = path
    logger.log('Modified PATH: '+path)

    with logger.frame('do_build'):
        process_modules(config_mods, 'do_build')
    with logger.frame('do_install'):
        process_modules(config_mods, 'do_install')
