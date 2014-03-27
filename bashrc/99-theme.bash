
export PS1="\[\e[00;33m\]\u\[\e[0m\]\[\e[00;37m\]@\h:\[\e[0m\]\[\e[00;36m\][\w]:\[\e[0m\]\[\e[00;37m\] \[\e[0m\]"

USERNAME="${yellow}\u${normal}"
HOST="${normal}\h${normal}"

WD="${cyan}[\w]${normal}"
VC="${red}(master)${normal}"
export PS1="$USERNAME@$HOST:$WD:$VC:"




case "$TERM" in
    xterm*|rxvt*)
	PS1="\[\e]0;\u@\h: \w\a\]$PS1"
	;;
    *)
	;;
esac



# from https://github.com/revans/bash-it/blob/master/themes/tylenol/tylenol.theme.bash
#!/usr/bin/env bash
#
# Based on 'bobby' theme with the addition of virtualenv_prompt
#

SCM_THEME_PROMPT_DIRTY=" ${red}✗"
SCM_THEME_PROMPT_CLEAN=" ${green}✓"
SCM_THEME_PROMPT_PREFIX=" ${yellow}|${reset_color}"
SCM_THEME_PROMPT_SUFFIX="${yellow}|"

RVM_THEME_PROMPT_PREFIX="|"
RVM_THEME_PROMPT_SUFFIX="|"
VIRTUALENV_THEME_PROMPT_PREFIX='|'
VIRTUALENV_THEME_PROMPT_SUFFIX='|'

function prompt_command() {
    PS1="\n${green}$(virtualenv_prompt)${red}$(ruby_version_prompt) ${reset_color}\h ${orange}in ${reset_color}\w\n${yellow}$(scm_char)$(scm_prompt_info) ${yellow}→${white} "
}

PROMPT_COMMAND=prompt_command;
