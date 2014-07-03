PROMPT_SYMBOL="${bash_prompt_normal}\$"
PROMPT_FORMAT="${bash_prompt_normal}"

USERNAME="${bash_prompt_yellow}\u"
HOST="${bash_prompt_normal}@\h"
WD="${bash_prompt_blue}[\w]"
TIME="${bash_prompt_bold_red}\t"


function prompt_command() {
	EXIT_STATUS=$?

	scm
	
	JOBS=`jobs -l`

	JOBS="$(echo "$JOBS" | perl -pe 's|(.+)Running\s+|\\[\\e[0;32m\\]\1 |g;' -pe 's|(.+)Stopped\s+|\\[\\e[0;31m\\]\1 |g;' -pe 's|(.+)Killed\s+|\\[\\e[0;35m\\]\1 |g;')"
	
	if [ $EXIT_STATUS == 0 ]; then
		EXIT_CODE=
	else
		EXIT_CODE="${bash_prompt_bold_white}${bash_prompt_background_red}!!! Exited: $EXIT_STATUS !!!"
	fi

	PS1="\n$JOBS\n$USERNAME$HOST $WD$SCM $TIME $EXIT_CODE${bash_prompt_normal}\n ${bash_prompt_normal}$PROMPT_SYMBOL $PROMPT_FORMAT"
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
