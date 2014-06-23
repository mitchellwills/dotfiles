from __future__ import absolute_import
import os
from build_util import *
from install_util import *


def build(obj, builddir):
    with open(os.path.join(builddir, '.emacs'), 'w') as f:
        emacs_file_spec = os.path.join(os.path.dirname(__file__), '*.emacs')
        f.write(concat_files(emacs_file_spec))

def install(obj, builddir):
    install_symlink_in_home('.emacs', os.path.join(builddir, '.emacs'))
