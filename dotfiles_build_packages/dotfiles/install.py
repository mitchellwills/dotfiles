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
import dotfiles.src_package as src_package
import dotfiles.logger as logger


BUILD_DIR_NAME = 'build'
SRC_DIR_NAME = 'src'
GIT_DIR_NAME = '.git'
BUILD_UTIL_DIR_NAME = 'dotfiles_build_packages'


def load_packages(path):
    packages = []
    action_factories = []
    package_factories = []
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
                        if thing.__module__ == 'dotfiles.package_base' or thing.__module__ == 'dotfiles.module_base' or thing.__module__ == 'dotfiles.src_package' or thing.__module__ == 'dotfiles.actions':
                            continue
                        if issubclass(thing, package_base.PackageBase):
                            if not is_abstract(thing):
                                logger.success('Loading package: '+filename+':'+name, verbose=True)
                                mod_found = True
                                package = thing()
                                packages.append(package)
                        if issubclass(thing, package_base.PackageActionFactory):
                            logger.success('Loading package action factory: '+filename+':'+name, verbose=True)
                            mod_found = True
                            action_factory = thing()
                            action_factories.append(action_factory)
                        if issubclass(thing, package_base.PackageFactory):
                            logger.success('Loading package factory: '+filename+':'+name, verbose=True)
                            mod_found = True
                            package_factory = thing()
                            package_factories.append(package_factory)
                if not mod_found:
                    logger.failed('No modules found in: '+filename)
            except IOError as e:
                logger.failed( 'Error loading module: '+str(e))
    return (packages, action_factories, package_factories)



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

        if config.local is None:
            config.assign('local', prompt_yes_no('install local'), float("inf"))


    packages = []
    action_factories = []
    package_factories = []
    with logger.frame('Loading packages'):
        for filename in os.listdir(rootdir):
            fullpath = os.path.join(rootdir, filename)
            if os.path.isdir(fullpath) and filename != BUILD_DIR_NAME and filename != BUILD_UTIL_DIR_NAME and not filename.startswith('.') and not filename == 'tools' and not filename == SRC_DIR_NAME:
                with logger.frame('Loading '+filename):
                    module_packages, module_action_factories, module_package_factories = load_packages(fullpath)
                    packages.extend(module_packages)
                    action_factories.extend(module_action_factories)
                    package_factories.extend(module_package_factories)

    global_context = module_base.GlobalContext(rootdir, srcdir, config, action_factories)

    action_factories.append(src_package.SrcPackageActionFactory())
    action_factories.append(package_base.SystemActionFactory())
    action_factories.append(package_base.NetPackageActionFactory())
    action_factories.append(package_base.ArchivePackageActionFactory())
    action_factories.append(package_base.FilePackageActionFactory())

    for factory in action_factories:
        factory.init_factory(global_context)

    logger.log('loaded package action factories: ' + str(names_of_items(action_factories)))
    logger.log('loaded package factories: ' + str(names_of_items(package_factories)))
    logger.log('loaded packages: ' + str(names_of_items(packages)))

    package_aliases = config.package_aliases

    # setup path for sub processes
    current_path = os.environ['PATH']
    path = ''
    if len(current_path) > 0:
        path = ':'+current_path
    path = ':'.join([os.path.expanduser(global_context.eval_templates(element)) for element in config.bash.path]) + path
    os.environ['PATH'] = path
    logger.log('Modified PATH: '+path)


    def resolve_package_alias(name):
        if name in package_aliases:
            return package_aliases[name]
        return name

    def resolve_package_aliases(names):
        result = map(resolve_package_alias, names)
        if type(names) is set:
            return set(result)
        return result

    def find_package(name):
        name = resolve_package_alias(name)
        if ':' in name:
            factory_name = name.split(':')[0]
            arg = name.split(':')[1]
            package_factory = find_by_name(package_factories, factory_name)
            if package_factory is None:
                raise Exception('Cannot resolve package factory name: ', factory_name)
            package = package_factory.build(arg)
        else:
            package = find_by_name(packages, name)
        if package is None:
            raise Exception('Cannot resolve package name: ', name)
        return package

    def order_by_dependancies(packages):
        install_steps = []
        remaining_packages = set(packages)
        evaluated = set()
        while True:
            evaluated_on_pass = set()
            remaining_configures = set()
            pass_steps = []
            for package in remaining_packages:
                remaining_configures |= resolve_package_aliases(object_configures(package))
            for package in remaining_packages:
                package_deps = resolve_package_aliases(object_deps(package))
                if evaluated.issuperset(package_deps) and package.name() not in remaining_configures:
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


    installing_packages = set()
    installing_package_names = set()
    unprocessed_package_names = set(config.install)
    unprocessed_packages = set()
    while len(unprocessed_package_names) > 0:
        for package_name in unprocessed_package_names:
            if package_name not in installing_package_names:
                package = find_package(package_name)
                unprocessed_packages.add(package)
        installing_package_names.update(map(resolve_package_alias, unprocessed_package_names))
        unprocessed_package_names.clear()
        for package in unprocessed_packages:
            package.init_package(global_context)
            unprocessed_package_names.update(object_deps(package))
            unprocessed_package_names.update(object_suggestions(package))
        installing_packages.update(unprocessed_packages)
        unprocessed_packages.clear()


    logger.log('Installing: ' + str(installing_package_names))

    package_install_state = dict()
    package_install_stages = order_by_dependancies(installing_packages)
    for package_stage in package_install_stages:
        with logger.frame('Installing: '+str(names_of_items(package_stage))):
            for package in package_stage:
                missing_deps = filter(lambda dep: package_install_state[dep] != 'installed', resolve_package_aliases(object_deps(package)))
                if len(missing_deps) is 0:
                    with logger.frame('Installing: '+package.name()):
                        try:
                            steps = package.install()
                            if steps is not None:
                                for step in steps:
                                    step()
                            else:
                                logger.failed('Install configuration did not return a list of steps')
                            package_install_state[package.name()] = 'installed'
                        except Exception as e:
                            logger.failed('Error installing ' + package.name() + ': ' + str(e))
                            package_install_state[package.name()] = 'install failed'
                else:
                    logger.warning('Skipped installing ' + package.name() + ', dependancies not met: ' + str(missing_deps))
                    package_install_state[package.name()] = 'skipped'
