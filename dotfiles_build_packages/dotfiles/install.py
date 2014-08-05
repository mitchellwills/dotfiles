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

def order_by_dependancies(packages):
    install_steps = []
    remaining_packages = set(packages)
    evaluated = set()
    while True:
        evaluated_on_pass = set()
        pass_steps = []
        for package in remaining_packages:
            package_deps = object_deps(package)
            if evaluated.issuperset(package_deps):
                pass_steps.append(package)
                evaluated_on_pass.add(package.name())

        evaluated.update(evaluated_on_pass)
        remaining_packages -= set(pass_steps)
        install_steps.append(pass_steps)

        if len(remaining_packages) == 0:
            break
        if len(evaluated_on_pass) == 0:
            raise Exception('unresolvable dependancies for: ', names_of_items(remaining_packages))
    return install_steps


def load_packages(path):
    packages = []
    action_factories = []
    files = all_files_recursive(path)
    name = os.path.basename(path)

    for filename in files:
        filepath = os.path.join(path, filename)
        if filename.endswith('~'):
            continue
        if filename.endswith('.pyc'):
            continue
        if not os.path.isfile(filepath):
            continue

        if filename.endswith('.py'):
            try:
                py_mod = load_py(name+'.'+filename.replace('.py', ''), filepath)
                mod_found = False
                for name in py_mod.__dict__:
                    thing = py_mod.__dict__[name]
                    if inspect.isclass(thing):
                        if thing.__module__ == 'dotfiles.package_base' or thing.__module__ == 'dotfiles.module_base' or thing.__module__ == 'dotfiles.actions':
                            continue
                        if issubclass(thing, package_base.PackageBase):
                            logger.success('Loading package: '+filename+':'+name, verbose=True)
                            mod_found = True
                            package = thing()
                            packages.append(package)
                        if issubclass(thing, package_base.PackageActionFactory):
                            logger.success('Loading package action factory: '+filename+':'+name, verbose=True)
                            mod_found = True
                            action_factory = thing()
                            action_factories.append(action_factory)
                if not mod_found:
                    logger.failed('No modules found in: '+filename)
            except IOError as e:
                logger.failed( 'Error loading module: '+str(e))
    return (packages, action_factories)



def main(rootdir):
    parser = argparse.ArgumentParser(description='Install dotfiles')
    parser.add_argument('--verbose', help="print verbose output", dest='verbose', action='store_true', default=False)

    args = parser.parse_args()
    logger.init(args.verbose)

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

        if config.install_local is None:
            config.assign('install_local', prompt_yes_no('install local'), float("inf"))


    packages = []
    action_factories = []
    with logger.frame('Loading packages'):
        for filename in os.listdir(rootdir):
            fullpath = os.path.join(rootdir, filename)
            if os.path.isdir(fullpath) and filename != BUILD_DIR_NAME and filename != BUILD_UTIL_DIR_NAME and not filename.startswith('.') and not filename == 'tools' and not filename == SRC_DIR_NAME:
                with logger.frame('Loading '+filename):
                    module_packages, module_action_factories = load_packages(fullpath)
                    packages.extend(module_packages)
                    action_factories.extend(module_action_factories)

    global_context = module_base.GlobalContext(rootdir, srcdir, config, action_factories)
    for package in packages:
        package.init_package(global_context)
    for factory in action_factories:
        factory.init_factory(global_context)


    logger.log('loaded package action factories: ' + str(names_of_items(action_factories)))
    logger.log('loaded packages: ' + str(names_of_items(packages)))

    packages_to_install = set()
    packages_to_install.update(filter(lambda package: package.name() in config.install, packages))
    logger.log('Installing: ' + str(names_of_items(packages_to_install)))

    packages_with_deps = set(packages_to_install)
    for package in packages_to_install:
        dep_names = object_deps(package)
        for dep_name in dep_names:
            dep = find_by_name(packages, dep_name)
            if dep is None:
                raise Exception('Cannot resolve dep: ', dep_name)
            packages_with_deps.add(dep)
    logger.log('Installing deps: ' + str(names_of_items(packages_with_deps)))

    package_install_stages = order_by_dependancies(packages_with_deps)
    for package_stage in package_install_stages:
        for package in package_stage:
            for step in package.install():
                step()

