#!/usr/bin/python
import os
import sys

BUILD_UTIL_DIR_NAME = 'dotfiles_build_packages'
rootdir = os.path.dirname(os.path.realpath(__file__))
buildutildir = os.path.join(rootdir, BUILD_UTIL_DIR_NAME)
sys.path.append(buildutildir)

import dotfiles.install

if __name__ == "__main__":
    dotfiles.install.main(rootdir)
