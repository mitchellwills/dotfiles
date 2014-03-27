#!/bin/sh

INPUT_DIR=$1
OUTPUT_DIR=$2

NAME=`basename $INPUT_DIR`


for file in `find $INPUT_DIR -type f ! -name 'build' ! -name '*~'`; do
	echo $file
	cat $file >> $OUTPUT_DIR/.$NAME.symlink;
done
