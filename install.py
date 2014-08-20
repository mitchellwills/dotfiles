#!/usr/bin/python
import os
import sys
import subprocess

version = sys.version_info
if version[0] <= 2 and version[1] < 7:
    print 'Bad python version: ' + str(version)
    print 'Atempting to execute with python2.7'
    new_args = list(sys.argv)
    new_args[0:1] = ['python2.7', os.path.realpath(__file__)]
    print 'executing: ', new_args
    subprocess.call(new_args)

else:
    rootdir = os.path.dirname(os.path.realpath(__file__))
    if rootdir not in sys.path:
        sys.path.append(rootdir)

    import dotfiles.install

    if __name__ == "__main__":
        dotfiles.install.main(rootdir)
