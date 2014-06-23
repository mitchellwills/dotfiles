from __future__ import absolute_import
import os
import shutil
from build_util import *
from install_util import *


def config(obj, config):
    if 'ros' in config.tags:
        obj.code('source ~/.rossetup')

def build(obj, builddir):
    shutil.copy2(os.path.join(os.path.dirname(__file__), '.rossetup'), os.path.join(builddir, '.rossetup'))

def install(obj, builddir):
    install_symlink_in_home('.rossetup', os.path.join(builddir, '.rossetup'))
