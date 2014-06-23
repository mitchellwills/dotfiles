from __future__ import absolute_import
import os

class BashCompletion:
    def __init__(self, d):
        self.d = d
    def build(self):
        return 'for f in '+os.path.join(self.d, '*')+'; do source $f; done'

def init(obj):
    obj.add_completion_dir = lambda completion_dir: obj.add_command(BashCompletion(completion_dir))

def config(obj, config):
    for completion_dir in config.bash.completion:
        obj.add_completion_dir(completion_dir)

