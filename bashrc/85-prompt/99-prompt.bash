PROMPT_SYMBOL="${normal}\$"
PROMPT_FORMAT="${normal}"

USERNAME="${yellow}\u"
HOST="${normal}@\h"
WD="${blue}[\w]"
TIME="${orange}\t"


function prompt_command() {
	EXIT_STATUS=$?

	[ -n "$TMUX" ] && tmux_env_update

	scm
	
	JOBS=`jobs -l`

	JOBS="$(echo "$JOBS" | perl -pe 's|(.+)Running\s+|\\[\\e[0;32m\\]\1 |g;' -pe 's|(.+)Stopped\s+|\\[\\e[0;31m\\]\1 |g;')"
	
	if [ $EXIT_STATUS == 0 ]; then
		EXIT_CODE=
	else
		EXIT_CODE="${white}${background_red}!!! Exited: $EXIT_STATUS !!!"
	fi

	PS1="\n$JOBS\n$USERNAME$HOST $WD$SCM $TIME $EXIT_CODE${normal}\n ${normal}$PROMPT_SYMBOL $PROMPT_FORMAT"
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
