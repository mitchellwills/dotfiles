from __future__ import absolute_import
from module_base import *
import os

class BashCompletion:
    def __init__(self, d):
        self.d = d
    def build(self):
        return 'for f in '+os.path.join(self.d, '*')+'; do source $f; done'

class BashrcCompletion(ModuleBase):
    def do_init(self):
        self.def_common('add_completion_dir', lambda completion_dir: self.add_command(BashCompletion(completion_dir)))

    def do_config(self):
        for completion_dir in self.config.bash.completion:
            self.add_completion_dir(completion_dir)

