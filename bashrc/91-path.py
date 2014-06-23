class BashPath:
    def __init__(self, var):
        self.path_entries = []
        self.var = var
    def build(self):
        if len(self.path_entries) > 0:
            new_path = ''
            for path_entry in self.path_entries:
                new_path = new_path + path_entry+':'
            new_path = new_path + '$'+self.var
            return 'export '+self.var+'='+new_path
        return ''

def init(obj):
    obj.bash_path = BashPath('PATH')
    obj.bash_ldpath = BashPath('LD_LIBRARY_PATH')
    obj.add_path = lambda path_entry: obj.bash_path.path_entries.append(path_entry)
    obj.add_ldpath = lambda path_entry: obj.bash_ldpath.path_entries.append(path_entry)

def config(obj, config):
    obj.add_command(obj.bash_path)
    obj.add_command(obj.bash_ldpath)

    for path in config.bash.path:
        obj.add_path(path)

    for path in config.bash.ldpath:
        obj.add_ldpath(path)

