from __future__ import absolute_import
import os
import shutil
from install_util import *


def build(obj, builddir):
    shutil.copy2(os.path.join(os.path.dirname(__file__), 'LS_COLORS'), os.path.join(builddir, '.dircolors'))

def install(obj, builddir):
    install_symlink_in_home('.dircolors', os.path.join(builddir, '.dircolors'))
