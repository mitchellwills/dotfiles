#!/bin/sh


config_path=`pwd`
echo $config_path
read -p "Use this as config directory (y/n)?" choice
case "$choice" in 
  y|Y ) continue;;
  n|N ) exit 1;;
  * ) exit 1;;
esac

unset install
read -p "Install stuff (y/n)?" choice
case "$choice" in 
  y|Y ) continue;;
  n|N ) install="no";;
  * ) exit 1;;
esac

(#subshell
    echo "Creating links"
    set -x #echo on

# Configure links
    ln -bf --symbolic ${config_path}/.bashrc ~/.bashrc
    ln -bf --symbolic ${config_path}/.emacs ~/.emacs
    ln -bf --symbolic ${config_path}/.gitconfig ~/.gitconfig
)

if [ -z $install ]
then
    (
	echo "Installing stuff"
	set -x #echo on
	sudo apt-get install sl
    )
fi


unset install config_path