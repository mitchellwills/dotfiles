#!/bin/sh


echo -n 'Enter path to config repo: '
read config_path
config_path=`readlink -f $config_path`

set -x #echo on

# Configure links
ln -f --symbolic ${config_path}/.bashrc ~/.bashrc
ln -f --symbolic ${config_path}/.emacs ~/.emacs
ln -f --symbolic ${config_path}/.gitconfig ~/.gitconfig
