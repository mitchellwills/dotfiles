

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth
# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000


# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"


function myps() { ps $@ -u $USER -o pid,%cpu,%mem,bsdtime,command ; }
function pstree() { myps f | awk '!/awk/ && $0~var' var=${1:-".*"} ; }


export LANG=UTF8


# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi


if [ -f ~/.rossetup ]; then
    source ~/.rossetup
fi

if [ -f ~/.local.bashrc ]; then
    source ~/.local.bashrc
fi


function r(){
	(
		cd "$(dirname "$(readlink ~/.bashrc)")/.."
		./install.sh
	)
	source ~/.bashrc
}
