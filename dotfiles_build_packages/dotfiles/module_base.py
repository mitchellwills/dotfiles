from __future__ import print_function
import os
import re
import inspect
import functools
import urllib2
import logger
import operator
import StringIO


class GlobalContext(object):
    def __init__(self, base_dir, src_dir, config):
        self.base_dir = base_dir
        self.src_dir = src_dir
        self.config = config

    def base_file(self, name):
        return os.path.join(self.base_dir, name)

    def src_file(self, name):
        return os.path.join(self.src_dir, name)

    def home_file(self, name):
        return os.path.expanduser(os.path.join('~/', name))

    def symlink(self, name, target_path):
        if os.path.lexists(name):
            if os.path.realpath(name) == target_path:
                logger.warning('symlink already exists ('+name+' -> '+target_path+')')
            else:
                with logger.trylog('backing up old file and createing symlink ('+name+' -> '+target_path+')'):
                    os.rename(name, name+'.bak');
                    os.symlink(target_path, name)
        else:
            with logger.trylog('createing symlink ('+name+' -> '+target_path+')'):
                os.symlink(target_path, name)



class ModuleCommon:
    def __init__(self):
        self.properties = dict()

class ModuleContext(object):
    def __init__(self, global_context, wd, builddir, module_common):
        self.global_context = global_context
        self.wd = wd
        self.builddir = builddir
        self.module_common = module_common
    def __getattr__(self, name):
        if name in self.module_common.properties:
            return self.module_common.properties[name]
        return getattr(self.global_context, name)

    def build_file(self, name):
        return os.path.join(self.builddir, name)

    def module_file(self, name):
        return os.path.join(self.wd, name)

    def amend_build_file(self, name, amendment):
        with open(self.build_file(name), 'a') as f:
            f.write(amendment)
    def amend_build_file_with_file(self, name, other_file):
        with open(other_file, 'r') as f:
            self.amend_build_file(name, f.read())

    def concatenate_files_to_build(self, files, build_file):
        for f in files:
            with logger.trylog('amending ' + f + ' -> ' + build_file, verbose=True):
                self.amend_build_file_with_file(build_file, f)

    def download_build_file(self, name, url):
        with logger.trylog('downloading ' + url + ' -> ' + name):
            response = urllib2.urlopen(url)
            contents = response.read()
            with open(self.build_file(name), 'w') as f:
                f.write(contents)

    def eval_template_content(self, match):
        template_content = match.group(1)
        if '\n' in template_content:
            content = StringIO.StringIO()
            scope = {"__builtins__": __builtins__, "config": self.config, "out": content}
            exec(template_content, scope)
            return content.getvalue()
        else:
            return eval(template_content, {"__builtins__": __builtins__, "config": self.config})

    def eval_templates(self, content):
        return re.sub('{{{{(.*?)}}}}', self.eval_template_content, content, flags=re.DOTALL)

    def eval_file_templates_to_build(self, input_file, out_name):
        with logger.trylog('evaluating templates ' + input_file + ' -> ' + out_name):
            open(self.build_file(out_name), 'w').write(self.eval_templates(open(input_file, 'r').read()))

class ModuleBase(object):
    def __init__(self, context):
        self.context = context
        self.config = context.config

    def __getattr__(self, name):
        return getattr(self.context, name)

    def def_common(self, name, value):
        if name in self.context.module_common.properties:
            raise Exception('Redefinition of ', name)
        self.context.module_common.properties[name] = value

def before(spec):
    def wrap(func):
        if not hasattr(func, 'before'):
            func.before = set()
        func.before.add(spec)
        return func
    return wrap
def after(spec):
    def wrap(func):
        if not hasattr(func, 'after'):
            func.after = set()
        func.after.add(spec)
        return func
    return wrap
