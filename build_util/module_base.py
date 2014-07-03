from __future__ import print_function
import os
import re
from install_util import *
import inspect
import functools

class BaseFileProcessor(object):
    def do_config(self, filepath, context):
        pass
    def do_build(self, filepath, context):
        pass
    def do_install(self, filepath, context):
        pass

class CustomFileProcessor(BaseFileProcessor):
    def __init__(self, config = None, build = None, install = None):
        self.config_func = config
        self.build_func = build
        self.install_func = install
        
    def do_config(self, filepath, context):
        if self.config_func is not None:
            self.config_func(filepath, context)
    def do_build(self, filepath, context):
        if self.build_func is not None:
            self.build_func(filepath, context)
    def do_install(self, filepath, context):
        if self.install_func is not None:
            self.install_func(filepath, context)

class HomeSymlinkFileProcessor(BaseFileProcessor):
    def __init__(self, name = None):
        self.name = name

    def do_install(self, filepath, context):
        if self.name is None:
            install_symlink_in_home(os.path.basename(filepath), filepath)
        else:
            install_symlink_in_home(self.name, filepath)
class AmendBuildFileProcessor(BaseFileProcessor):
    def __init__(self, build_filename = None):
        self.build_filename = build_filename

    def do_build(self, filepath, context):
        context.amend_build_file_with_file(self.build_filename, filepath)

class ModuleContext(object):
    def __init__(self, wd, builddir, config, common):
        self.wd = wd
        self.builddir = builddir
        self.config = config
        self.common = common

    def build_file(self, name):
        return os.path.join(self.builddir, name)

    def amend_build_file(self, name, amendment):
        with open(self.build_file(name), 'a') as f:
            f.write(amendment)
    def amend_build_file_with_file(self, name, other_file):
        with open(other_file, 'r') as f:
            self.amend_build_file(name, f.read())

    
class ModuleCommon:
    def __init__(self):
        self.properties = dict()
        self.file_processors = dict()
    

class ModuleBase(object):
    def __init__(self, context):
        self.context = context
        self.config = context.config

    def __getattr__(self, name):
        if name in ModuleContext.__dict__:
            return lambda *args, **kwargs: ModuleContext.__dict__[name](self.context, *args, **kwargs)
        return self.context.common.properties[name]

    def def_common(self, name, value):
        if name in self.context.common.properties:
            raise Exception('Redefinition of ', name)
        self.context.common.properties[name] = value

    def file_path_regex_matcher(self, regex):
        return lambda filepath: re.match(regex, filepath)
        
    def def_file_processor(self, matcher, processor):
        self.context.common.file_processors[matcher] = processor
    def def_file_processor_for_regex_match(self, regex, processor):
        self.def_file_processor(self.file_path_regex_matcher(regex), processor)
    #TODO actually make this match only a file 
    def def_file_processor_for_file(self, filename, processor):
        self.def_file_processor_for_regex_match('.+/'+filename, processor)
        
    def get_file_processor(self, filepath):
        selected_processor = None
        for matcher in self.context.common.file_processors:
            if matcher(filepath):
                processor = self.context.common.file_processors[matcher]
                if selected_processor is not None:
                    raise Exception('Multiple file processors found for: '+filepath)
                selected_processor = processor
        if selected_processor is None:
            raise Exception('No file processor found for: '+filepath)
        return selected_processor
    

    def do_init(self):
        pass
    def do_config(self):
        pass
    def do_build(self):
        pass
    def do_install(self):
        pass

