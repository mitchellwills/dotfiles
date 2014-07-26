from __future__ import absolute_import
import os
from build_util import *
from module_base import *
import logger

class UiSettings(ModuleBase):
    def do_install(self):
        if self.config.uisettings.canonical_scroll:
            with logger.trylog('Setting normal scroll mode'):
                os.system('gsettings set com.canonical.desktop.interface scrollbar-mode normal')
        if self.config.uisettings.nonrecursive_search:
            with logger.trylog('Disabling recursive search'):
                os.system('gsettings set org.gnome.nautilus.preferences enable-interactive-search true')
