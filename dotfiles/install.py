#!/usr/bin/python
from __future__ import absolute_import
import os
import shutil
import sys
import glob
import argparse
import inspect

from dotfiles.config import ConfigLoader
from dotfiles.util import *
import dotfiles.package_base as package_base
import dotfiles.actions as actions
import dotfiles.src_package as src_package
import dotfiles.logger as logger
from collections import defaultdict
from spgl.relational_database import *

__abstract__ = True
__all__ = ['main']

BUILD_DIR_NAME = 'build'
SRC_DIR_NAME = 'src'
GIT_DIR_NAME = '.git'
BUILD_UTIL_DIR_NAME = 'dotfiles_build_packages'

class PackageRelationship(object):
    CONFIGURED_BY = Relationship('configured by')
    CONFIGURES = Relationship('configures')
    make_inverse_relationships(CONFIGURED_BY, CONFIGURES)

    DEPENDED_ON_BY = Relationship('depended on by')
    DEPENDS_ON = Relationship('depends on')
    make_inverse_relationships(DEPENDED_ON_BY, DEPENDS_ON)

    SUGGESTED_BY = Relationship('suggested by')
    SUGGESTS = Relationship('suggests')
    make_inverse_relationships(SUGGESTED_BY, SUGGESTS)

class PackageState:
    UNINITIALIZED = 'uninitialized'
    INITIALIZED = 'initialized'
    INSTALLED = 'installed'
    NOT_INSTALLABLE = 'not installable'
    DEPS_NOT_SATISFIED = 'deps not satisfied'
    INSTALL_FAILED = 'install failed'
    ALL = [UNINITIALIZED, INITIALIZED, DEPS_NOT_SATISFIED, INSTALLED, NOT_INSTALLABLE, INSTALL_FAILED]

    @staticmethod
    def could_install(state):
        return state == PackageState.INITIALIZED

class PackageInfo(RelationalDatabaseNode):
    def __init__(self, name):
        super(PackageInfo, self).__init__(name)
        self.install_steps = None
        self.state = PackageState.UNINITIALIZED
        self.state_message = None
        self.state_error = None

    @property
    def name(self):
        return self.key

class PackageCollection(object):
    def __init__(self, context, raw_packages, package_factories):
        self.packages = RelationalDatabase()
        self.context = context
        self.raw_packages = raw_packages
        self.package_factories = package_factories

        for package_name in self.context.config.packages.keys():
            package_config = self.context.config.packages[package_name]
            package_name = self.resolve_package_alias(package_name)
            package_info = self.ensure_package(package_name)
            if 'deps' in package_config:
                for dep_name in self.resolve_package_aliases(package_config.deps):
                    self.add_package(dep_name)
                    package_info.add_relationship(PackageRelationship.DEPENDS_ON, dep_name)
            if 'suggests' in package_config:
                for suggest_name in self.resolve_package_aliases(package_config.suggests):
                    self.add_package(suggest_name)
                    package_info.add_relationship(PackageRelationship.SUGGESTS, suggest_name)
            if 'configures' in package_config:
                for configures_name in self.resolve_package_aliases(package_config.configures):
                    self.ensure_package(configures_name)
                    package_info.add_relationship(PackageRelationship.CONFIGURES, configures_name)


    def resolve_package_alias(self, name):
        if name in self.context.config.package_aliases:
            return self.context.config.package_aliases[name]
        return name

    def resolve_package_aliases(self, names):
        result = map(self.resolve_package_alias, names)
        if type(names) is set:
            return set(result)
        return result

    def ensure_package(self, name):
        if name not in self.packages:
            self.packages.add_node(PackageInfo(name))
        return self.packages[name]

    def add_package(self, name):
        name = self.resolve_package_alias(name)
        if name not in self.packages or self.packages[name].state == PackageState.UNINITIALIZED:
            if ':' in name:
                factory_name = name.split(':')[0]
                arg = name.split(':')[1]
                package_factory = find_by_name(self.package_factories, factory_name)
                if package_factory is None:
                    raise Exception('Cannot resolve package factory name: '+factory_name+' for package: '+name)
                package = package_factory.build(arg)
            else:
                package = find_by_name(self.raw_packages, name)
            if package is None:
                raise Exception('Could not find package: '+name)

            package_info = self.ensure_package(package.name())
            try:
                package.init_package(self.context)

                package_info.install_steps = package.install()
                if package_info.install_steps is None:
                    package_info.state_message = 'No install steps returned'
                    package_info.state = PackageState.NOT_INSTALLABLE
                else:
                    package_info.state = PackageState.INITIALIZED
                    for step in package_info.install_steps:
                        for dep_name in self.resolve_package_aliases(object_deps(step)):
                            self.add_package(dep_name)
                            package_info.add_relationship(PackageRelationship.DEPENDS_ON, dep_name)

                for dep_name in self.resolve_package_aliases(object_deps(package)):
                    self.add_package(dep_name)
                    package_info.add_relationship(PackageRelationship.DEPENDS_ON, dep_name)
                for suggest_name in self.resolve_package_aliases(object_suggestions(package)):
                    self.add_package(suggest_name)
                    package_info.add_relationship(PackageRelationship.SUGGESTS, suggest_name)
                for configures_name in self.resolve_package_aliases(object_configures(package)):
                    self.ensure_package(configures_name)
                    package_info.add_relationship(PackageRelationship.CONFIGURES, configures_name)
            except Exception as e:
                package_info.state_error = e
                package_info.state_message = 'Error configuring package'
                package_info.state = PackageState.NOT_INSTALLABLE




    def get_installable_packages(self):
        installable_packages = set()
        for package_name in self.packages.keys():
            package_info = self.packages[package_name]
            if package_info.state == PackageState.INITIALIZED:
                deps_satisfied = True
                for dep in package_info.get_related(PackageRelationship.DEPENDS_ON):
                    if dep.state != PackageState.INSTALLED:
                        deps_satisfied = False
                configured_satisfied = True
                for dep in package_info.get_related(PackageRelationship.CONFIGURED_BY):
                    if PackageState.could_install(dep.state):
                        configured_satisfied = False
                if deps_satisfied and configured_satisfied:
                    installable_packages.add(package_info)
        return installable_packages

    def propagate_package_state(self):
        action_taken = True
        while action_taken:
            action_taken = False
            for package_name in self.packages.keys():
                package_info = self.packages[package_name]
                if package_info.state == PackageState.INITIALIZED:
                    for dep in package_info.get_related(PackageRelationship.DEPENDS_ON):
                        if dep.state == PackageState.NOT_INSTALLABLE or dep.state == PackageState.DEPS_NOT_SATISFIED:
                            package_info.state = PackageState.DEPS_NOT_SATISFIED
                            package_info.state_message = 'Dep \''+dep.name+'\' is not installable'
                            action_taken = True
                        elif dep.state == PackageState.INSTALL_FAILED:
                            package_info.state = PackageState.DEPS_NOT_SATISFIED
                            package_info.state_message = 'Dep \''+dep.name+'\' failed to install'
                            action_taken = True


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

        if filename.endswith('__init__.py'):
            continue
        if filename.endswith('.py'):
            try:
                py_mod = load_py(name+'.'+filename.replace('.py', ''), filepath)
                mod_found = False
                for name in py_mod.__dict__:
                    thing = py_mod.__dict__[name]
                    if inspect.isclass(thing):
                        if thing.__module__ != py_mod.__name__:
                            continue
                        if not is_abstract(thing):
                            if issubclass(thing, package_base.PackageBase):
                                logger.success('Loading package: '+filename+':'+name, verbose=True)
                                mod_found = True
                                package = thing()
                                packages.append(package)
                            elif issubclass(thing, actions.PackageActionFactory):
                                logger.success('Loading package action factory: '+filename+':'+name, verbose=True)
                                mod_found = True
                                action_factory = thing()
                                action_factories.append(action_factory)
                            elif issubclass(thing, package_base.PackageFactory):
                                logger.success('Loading package factory: '+filename+':'+name, verbose=True)
                                mod_found = True
                                package_factory = thing()
                                package_factories.append(package_factory)
                            else:
                                logger.warning('Did not load class: ' + str(thing) + ': ' + str(thing.__bases__), verbose=True)
                if not mod_found and not is_abstract(py_mod):
                    logger.failed('No modules found in: '+filename)
            except IOError as e:
                logger.failed( 'Error loading module: '+str(e))
    return (packages, action_factories, package_factories)



def main(rootdir):
    parser = argparse.ArgumentParser(description='Install dotfiles')
    parser.add_argument('--verbose', help="print verbose output", dest='verbose', action='store_true', default=False)
    parser.add_argument('--clean', help="do a clean build of source repos", dest='clean', action='store_true', default=False)

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
        files = all_files_recursive(rootdir) + all_files_recursive(os.path.expanduser("~/.dotfiles-personal"))
        conf_files = filter(lambda f: f.endswith('.conf') and not f.startswith(srcdir), files)
        for f in conf_files:
            with logger.trylog('loading conf: '+f):
                config_loader.load_file(f)
        with logger.trylog('loading user conf file'):
            config_loader.load_file(os.path.expanduser('~/.dotfiles.conf'))


        config = config_loader.build()

        if 'local' not in config:
            config.assign('local', prompt_yes_no('install local'), float("inf"))

        if args.clean:
            config.assign('src.clean_src', True, float("inf"))

        config.src.add('make_args', '-j'+config.system.cpu_count, -1)

    raw_packages = []
    action_factories = []
    package_factories = []
    with logger.frame('Loading packages'):
        for filename in os.listdir(rootdir):
            fullpath = os.path.join(rootdir, filename)
            if os.path.isdir(fullpath) and not filename.startswith('.') and not filename == SRC_DIR_NAME and not filename == BUILD_DIR_NAME:
                with logger.frame('Loading '+filename):
                    module_packages, module_action_factories, module_package_factories = load_packages(fullpath)
                    raw_packages.extend(module_packages)
                    action_factories.extend(module_action_factories)
                    package_factories.extend(module_package_factories)

    global_context = package_base.GlobalContext(rootdir, srcdir, config, action_factories)

    for factory in action_factories:
        factory.init_factory(global_context)

    logger.log('loaded package action factories: ' + str(names_of_items(action_factories)))
    logger.log('loaded package factories: ' + str(names_of_items(package_factories)))
    logger.log('loaded raw packages: ' + str(names_of_items(raw_packages)))

    package_aliases = config.package_aliases

    # setup path for sub processes
    def configure_env_path(name, new_elements):
        if name in os.environ:
            current_path = os.environ[name]
        else:
            current_path = ''
        path = ''
        if len(current_path) > 0:
            path = ':'+current_path
        path = ':'.join([os.path.expanduser(global_context.eval_templates(element)) for element in new_elements]) + path
        os.environ[name] = path
        logger.log('Modified '+name+': '+path)

    configure_env_path('PATH', config.env.path)
    configure_env_path('LIBRARY_PATH', config.env.library_path)
    configure_env_path('LD_LIBRARY_PATH', config.env.ld_library_path)
    configure_env_path('CPATH', config.env.cpath)
    configure_env_path('PYTHONPATH', config.env.pythonpath)

    packages = PackageCollection(global_context, raw_packages, package_factories)
    for package_name in config.install:
        packages.add_package(package_name)


    for installable_packages in iter(packages.get_installable_packages, set()):
        with logger.frame('Installing: '+str(names_of_items(installable_packages))):
            for package_info in installable_packages:
                with logger.frame('Installing: '+package_info.name):
                    try:
                        for step in package_info.install_steps:
                            step()
                        package_info.state = PackageState.INSTALLED
                    except Exception as e:
                        package_info.state = PackageState.INSTALL_FAILED
                        package_info.state_error = e
                        logger.failed(str(e))
                        if args.verbose:
                            raise
            packages.propagate_package_state()

    for state in PackageState.ALL:
        state_items = filter(lambda node: node.state == state, packages.packages.nodes())
        if len(state_items) > 0:
            with logger.frame(state):
                for package_info in state_items:
                    frame = package_info.name
                    if package_info.state_message is not None:
                        frame = frame + ': ' + package_info.state_message
                    with logger.frame(frame):
                        if package_info.state_error is not None:
                            logger.log('Error: '+str(package_info.state_error))
