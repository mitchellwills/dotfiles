from __future__ import absolute_import
from dotfiles.package_base import *

@configures('bashrc')
class rossetup(PackageBase):
    def configure_bashrc(self):
        self.config.bash.ensure('parts')
        self.config.bash.parts.assign('95-ros', 'source ~/.rossetup\n')

    def eval_template(self):
        rossetup_script = self.eval_templates(read_file(self.base_file('ros/.rossetup')))
        with open(self.build_file('.rossetup'), 'w') as f:
            f.write(rossetup_script)

    def install(self):
        return concat_lists(
            [self.configure_bashrc],
            [self.eval_template],
            self.action('file').symlink(self.home_file('.rossetup'), self.build_file('.rossetup'))
        )

