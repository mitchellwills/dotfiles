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

from config_util import ConfigLoader
from build_util import *
import module_base
import logger


BUILD_DIR_NAME = 'build'
SRC_DIR_NAME = 'src'
GIT_DIR_NAME = '.git'

def load_py(name, path):
    return imp.load_source(name, path)

def process_modules(config_mods, func_name):
    # import function
    dependancies = dict()
    for mod in config_mods:
        mod_name = mod.__class__.__name__
        if hasattr(mod, func_name):
            func = getattr(mod, func_name)
            dependancies[mod_name] = func
            if not hasattr(func, 'after'):
                func.__func__.after = set()

    # move items from before to the coresponding after
    for mod_name in dependancies:
        func = dependancies[mod_name]
        if hasattr(func, 'before'):
            for build_dep in func.before:
                if build_dep not in dependancies:
                    raise Exception('No module found: ' + build_dep + ', was dep for ' + mod_name)
                else:
                    dependancies[build_dep].after.add(mod_name)

    # evaluate steps respecting dependancies
    evaluated = set()
    while True:
        evaluated_on_pass = set()
        for mod_name in dependancies:
            func = dependancies[mod_name]
            if evaluated.issuperset(func.after):
                with logger.frame(mod_name+'.'+func_name+': '+str(list(func.after))):
                    func()
                    evaluated_on_pass.add(mod_name)

        evaluated.update(evaluated_on_pass)
        for mod_name in evaluated_on_pass:
            dependancies.pop(mod_name)

        if len(dependancies) == 0:
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
                    if name == 'ModuleBase':
                        continue
                    thing = py_mod.__dict__[name]
                    #TODO figure out how to do class type instead of this
                    if isinstance(thing, type(module_base.ModuleBase)) and issubclass(thing, module_base.ModuleBase):
                        logger.success('Loading module: '+filename+':'+name)
                        mod_found = True
                        config_mods.append(thing(context))
                if not mod_found:
                    logger.failed('No modules found in: '+filename)
            except IOError as e:
                logger.failed( 'Error loading module: '+str(e))



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
    parser.add_argument('--upgrade', help="run apt-get upgrade", dest='upgrade', action='store_true', default=False)

    args = parser.parse_args()
    logger.log(args)

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

    global_context = module_base.GlobalContext(rootdir, config)

    with logger.frame('Loading Modules'):
        config_mods = []
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

if __name__ == "__main__":
    main()



