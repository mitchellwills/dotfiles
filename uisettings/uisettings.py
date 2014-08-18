from __future__ import absolute_import
import os
from dotfiles.package_base import PackageBase
import dotfiles.logger as logger

class uisettings(PackageBase):
    def install(self):
        actions = []
        if self.config.uisettings.canonical_scroll:
            actions.extend(self.action('system').command(['gsettings', 'set', 'com.canonical.desktop.interface', 'scrollbar-mode', 'normal']))
        if self.config.uisettings.nonrecursive_search:
            actions.extend(self.action('system').command(['gsettings', 'set', 'org.gnome.nautilus.preferences', 'enable-interactive-search', 'true']))
        return actions
