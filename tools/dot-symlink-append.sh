#!/bin/sh

INPUT_DIR=$1
OUTPUT_DIR=$2

NAME=`basename $INPUT_DIR`
OUT_FILE=$OUTPUT_DIR/.$NAME.symlink

FILES=`find $INPUT_DIR -type f ! -name 'build' ! -name '*~' | sort`

for file in $FILES; do
	echo "	$file"
	cat $file >> $OUT_FILE;
done
