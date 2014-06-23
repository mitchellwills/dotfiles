def init(obj):
    obj.add_alias = lambda name, value, comment = None: obj.add_config('alias.'+name, value, comment)

def config(obj, config):
    obj.add_alias('tree', "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cblue[%cn] %Cgreen(%cr)%Creset' --abbrev-commit --date=relative")
    obj.add_alias('lol',  "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cblue[%cn] %Cgreen(%cr)%Creset' --abbrev-commit --date=relative")
    obj.add_alias('lola', "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cblue[%cn] %Cgreen(%cr)%Creset' --abbrev-commit --date=relative --all")

    obj.add_alias('publish', '!sh -c \"git push -u origin $(git rev-parse --abbrev-ref HEAD)\"', 'pushes a new branch to origin')

    obj.add_alias('cp', "cherry-pick")
    obj.add_alias('st', "status -s -b")
    obj.add_alias('cl', "clone")
    obj.add_alias('ci', "commit")
    obj.add_alias('cia', "commit -a")
    obj.add_alias('co', "checkout")
    obj.add_alias('br', "branch")
    obj.add_alias('diff', "diff --word-diff")
    obj.add_alias('dc', "diff --cached")
    obj.add_alias('unstage', "reset HEAD --")
