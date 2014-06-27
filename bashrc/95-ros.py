from __future__ import absolute_import
import os
import shutil
from build_util import *
from install_util import *


def config(obj, config):
    if config.ros.install:
        obj.code('source ~/.rossetup')
        obj.install = True
    else:
        obj.install = False

def build(obj, builddir):
    if obj.install:
        shutil.copy2(os.path.join(os.path.dirname(__file__), '.rossetup'), os.path.join(builddir, '.rossetup'))

def install(obj, builddir):
    if obj.install:
        install_symlink_in_home('.rossetup', os.path.join(builddir, '.rossetup'))
