# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

#shell options
shopt -s cdspell
shopt -s cmdhist
shopt -s extglob

#disable flow control ^S and ^Q
stty -ixon
