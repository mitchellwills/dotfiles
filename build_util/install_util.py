import os
import logger

def install_symlink(installed_file, target_path):
    if os.path.lexists(installed_file):
        if os.path.realpath(installed_file) == target_path:
            logger.warning('symlink already exists ('+installed_file+' -> '+target_path+')')
        else:
            with logger.trylog('backing up old file and createing symlink ('+installed_file+' -> '+target_path+')'):
                os.rename(installed_file, installed_file+'.bak');
                os.symlink(target_path, installed_file)
    else:
        with logger.trylog('createing symlink ('+installed_file+' -> '+target_path+')'):
            os.symlink(target_path, installed_file)

def install_symlink_in_home(installed_relative_path, target_path):
    installed_file = os.path.expanduser(os.path.join('~/', installed_relative_path))
    install_symlink(installed_file, target_path)
