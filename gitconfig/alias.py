from __future__ import absolute_import
from module_base import *


class GitConfigAlias(ModuleBase):
    def do_init(self):
        self.def_common('add_alias', lambda name, value, comment = None: self.add_config('alias.'+name, value, comment))

    def do_config(self):
        self.add_alias('tree', "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cblue[%cn] %Cgreen(%cr)%Creset' --abbrev-commit --date=relative")
        self.add_alias('lol',  "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cblue[%cn] %Cgreen(%cr)%Creset' --abbrev-commit --date=relative")
        self.add_alias('lola', "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cblue[%cn] %Cgreen(%cr)%Creset' --abbrev-commit --date=relative --all")

        self.add_alias('publish', '!sh -c \"git push -u origin $(git rev-parse --abbrev-ref HEAD)\"', 'pushes a new branch to origin')

        self.add_alias('cp', "cherry-pick")
        self.add_alias('st', "status -s -b")
        self.add_alias('cl', "clone")
        self.add_alias('ci', "commit")
        self.add_alias('cia', "commit -a")
        self.add_alias('co', "checkout")
        self.add_alias('br', "branch")
        self.add_alias('diff', "diff --word-diff")
        self.add_alias('dc', "diff --cached")
        self.add_alias('unstage', "reset HEAD --")
