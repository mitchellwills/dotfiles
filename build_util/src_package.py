import logger
import os

class SrcRepo(object):
    pass

class GitRepo(SrcRepo):
    def __init__(self, path, branch = None):
        self.path = path
        self.branch = branch
    def update(self, directory):
        if os.path.isdir(directory):
            os.system('cd "'+directory+'"; git fetch')
        else:
            os.system('git clone "'+self.path+'" "'+directory+'"')
        if self.branch is not None:
            os.system('cd "'+directory+'"; git checkout '+self.branch)
    def clean(self, directory):
        os.system('cd "'+directory+'"; git clean -xdf')


class SrcPackage(object):
    def __init__(self, name, src_repo, module):
        self.name = name
        self.src_repo = src_repo
        self.module = module
        self.src_dir = self.module.src_file(self.name)

    def update(self):
        if os.path.isdir(self.src_dir) and self.module.config.src.clean_src:
            with logger.trylog('Cleaning Src: '+self.name):
                self.src_repo.clean(self.src_dir)
        with logger.trylog('Updating Src: '+self.name):
            self.src_repo.update(self.src_dir)

    def configure(self, prefix = None):
        with logger.trylog('Configuring Src: '+self.name):
            configure_command = './configure'
            if prefix is not None:
                configure_command += ' --prefix="'+os.path.expanduser(prefix)+'"'
            os.system('cd "'+self.src_dir+'"; '+configure_command)

    def make_install(self):
        with logger.trylog('Make Installing Src: '+self.name):
            os.system('cd "'+self.src_dir+'"; make install '+self.module.config.src.make_args)

