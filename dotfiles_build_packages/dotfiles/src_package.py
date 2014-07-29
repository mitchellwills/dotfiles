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
            logger.call(['git', 'fetch'], cwd=directory)
        else:
            logger.call(['git', 'clone', self.path, directory])
        if self.branch is not None:
            logger.call(['git', 'checkout', self.branch], cwd=directory, output_handler=logger.log_stderr)
    def clean(self, directory):
        logger.call(['git', 'clean', '-xdf'], cwd=directory)

class SrcPackage(object):
    def __init__(self, name, src_repo, context):
        self.name = name
        self.src_repo = src_repo
        self.context = context
        self.src_dir = self.context.src_file(self.name)

    def update(self):
        if os.path.isdir(self.src_dir) and self.context.config.src.clean_src:
            with logger.frame('Cleaning Src: '+self.name):
                self.src_repo.clean(self.src_dir)
        with logger.frame('Updating Src: '+self.name):
            self.src_repo.update(self.src_dir)

    def configure(self, prefix = None):
        with logger.frame('Configuring Src: '+self.name):
            configure_command = ['./configure']
            if prefix is not None:
                configure_command.append('--prefix='+os.path.expanduser(prefix))
            logger.call(configure_command, cwd=self.src_dir)

    def make_install(self):
        with logger.frame('Make Installing Src: '+self.name):
            command = ['make', 'install']
            if self.context.config.src.make_args is not None:
                command.extend(self.context.config.src.make_args)
            logger.call(command, cwd=self.src_dir)

