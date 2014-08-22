from __future__ import absolute_import
from dotfiles.util import *
from dotfiles.module_base import *
import dotfiles.logger as logger

__abstract__ = True

@abstract
class PackageFactory(object):
    pass

@abstract
class PackageBase(object):
    def __init__(self):
        self.context = None

    def init_package(self, context):
        self.context = context

    def __getattr__(self, name):
        if self.context is None:
            raise Exception('Package not yet initialized')
        return getattr(self.context, name)

    def name(self):
        return type(self).__name__

    def __str__(self):
        return 'package('+self.name()+')'
    def __name__(self):
        return self.__str__()
    def __repr__(self):
        return self.__str__()

    def install(self):
        logger.failed('No install for '+self.name())
        return None



BUILD_DIR_NAME = 'build'
SRC_DIR_NAME = 'src'

class GlobalContext(object):
    def __init__(self, base_dir, src_dir, config, action_factories):
        self.base_dir = base_dir
        self.src_dir = src_dir
        self.config = config
        self.action_factories = action_factories

    def base_file(self, name):
        return os.path.join(self.base_dir, name)

    def src_file(self, name):
        return os.path.join(self.base_file(SRC_DIR_NAME), name)

    def build_file(self, name):
        return os.path.join(self.base_file(BUILD_DIR_NAME), name)

    def home_file(self, name):
        return os.path.expanduser(os.path.join('~/', name))

    def action(self, name):
        result = find_by_name(self.action_factories, name)
        if result is None:
            raise Exception('Could not find action factory: '+name)
        return result

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
