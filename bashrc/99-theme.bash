

# from https://github.com/revans/bash-it/blob/master/themes/tylenol/tylenol.theme.bash
#!/usr/bin/env bash
#
# Based on 'bobby' theme with the addition of virtualenv_prompt
#

SCM_THEME_PROMPT_PREFIX=" ${yellow}|${reset_color}"
SCM_THEME_PROMPT_SUFFIX="${yellow}|"

RVM_THEME_PROMPT_PREFIX="|"
RVM_THEME_PROMPT_SUFFIX="|"
VIRTUALENV_THEME_PROMPT_PREFIX='|'
VIRTUALENV_THEME_PROMPT_SUFFIX='|'

test=$'\xE2\x8E\x87'
test=$'\xe2\x88\xb4 \xe2\x86\x92 \xe2\x98\xb \xe2\x98\x85'

function prompt_command() {
    PS1="\n${green}$(virtualenv_prompt)${red}$(ruby_version_prompt) ${reset_color}\h ${orange}in ${reset_color}\w\n${yellow}$(scm_char) $test$(scm_prompt_info) ${yellow}→:${white} "
}

#PROMPT_COMMAND=prompt_command;

SCM_SYMBOL=$'±'
SCM_DIRTY="${red}✗"
SCM_CLEAN="${green}✓"

RIGHT_ARROW_SYMBOL=$'\xe2\x86\x92'

PROMPT_SYMBOL="${normal}\$"
PROMPT_FORMAT="${normal}"

USERNAME="${yellow}\u"
HOST="${normal}\h"
WD="${blue}[\w]"


function git_prompt_vars {
  SCM_GIT_AHEAD=''
  SCM_GIT_BEHIND=''
  SCM_GIT_STASH=''
  local status="$(git status -bs --porcelain 2> /dev/null)"
  if [[ -n "$(grep -v ^# <<< "${status}")" ]]; then
    SCM_DIRTY=1
    SCM_STATE=${GIT_THEME_PROMPT_DIRTY:-$SCM_THEME_PROMPT_DIRTY}
  else
    SCM_DIRTY=0
    SCM_STATE=${GIT_THEME_PROMPT_CLEAN:-$SCM_THEME_PROMPT_CLEAN}
  fi
  SCM_PREFIX=${GIT_THEME_PROMPT_PREFIX:-$SCM_THEME_PROMPT_PREFIX}
  SCM_SUFFIX=${GIT_THEME_PROMPT_SUFFIX:-$SCM_THEME_PROMPT_SUFFIX}
  local ref=$(git symbolic-ref HEAD 2> /dev/null)
  SCM_BRANCH=${ref#refs/heads/}
  SCM_CHANGE=$(git rev-parse HEAD 2>/dev/null)
  local ahead_re='.+ahead ([0-9]+).+'
  local behind_re='.+behind ([0-9]+).+'
  [[ "${status}" =~ ${ahead_re} ]] && SCM_GIT_AHEAD=" ${SCM_GIT_AHEAD_CHAR}${BASH_REMATCH[1]}"
  [[ "${status}" =~ ${behind_re} ]] && SCM_GIT_BEHIND=" ${SCM_GIT_BEHIND_CHAR}${BASH_REMATCH[1]}"
  local stash_count="$(git stash list 2> /dev/null | wc -l | tr -d ' ')"
  [[ "${stash_count}" -gt 0 ]] && SCM_GIT_STASH=" {${stash_count}}"
}
function scm {
  if [[ -f .git/HEAD ]]; then SCM=$SCM_GIT
  elif which git &> /dev/null && [[ -n "$(git symbolic-ref HEAD 2> /dev/null)" ]]; then SCM=$SCM_GIT
  elif [[ -d .hg ]]; then SCM=$SCM_HG
  elif which hg &> /dev/null && [[ -n "$(hg root 2> /dev/null)" ]]; then SCM=$SCM_HG
  elif [[ -d .svn ]]; then SCM=$SCM_SVN
  else SCM=$SCM_NONE
  fi
}


function prompt_command() {
	EXIT_STATUS=$?
	SCM_STATUS="$SCM_DIRTY"
	SCM="${green}|${green}master $SCM_STATUS${green}|"
	
	if [ $(jobs | wc -l) = 0 ]; then
		JOBS=
	else
		LAST_JOB=`jobs | awk '/^\[[0-9]+\]\+/ {print $3}'`
		JOBS="${cyan}[\j∴$LAST_JOB]"
	fi
	
	if [ $EXIT_STATUS == 0 ]; then
		EXIT_CODE=
	else
		EXIT_CODE="${white}${background_red}Exited: $EXIT_STATUS"
	fi

	PS1="\n$USERNAME@$HOST $WD $SCM $JOBS $EXIT_CODE\n$PROMPT_SYMBOL $PROMPT_FORMAT"
	# set title bar
	case "$TERM" in
	    xterm*|rxvt*)
		PS1="\[\e]0;\u@\h: \w\a\]$PS1"
		;;
	    *)
		;;
	esac
	
}

PROMPT_COMMAND=prompt_command;
