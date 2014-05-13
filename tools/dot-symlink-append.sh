#!/bin/bash

INPUT_DIR=$1
INPUT_NAME=$2
OUTPUT_DIR=$3
ROOT_DIR=$4
shift 4
SYSTEM_TAGS="${@}"

OUT_FILE=$OUTPUT_DIR/.$INPUT_NAME.symlink

FILES=`find $INPUT_DIR -type f ! -name 'build' ! -name '*~' | sort`

for file in $FILES; do
	FILE_NAME=`basename $file`
	FILE_TAGS=$(echo "$FILE_NAME" | grep -o -E '\([^\)]+\)' | sed -r 's/\((.+)\)/\1/')
	FILE_NAME_WITHOUT_TAGS=`$ROOT_DIR/tools/contains_tags.py $FILE_NAME $SYSTEM_TAGS`
	INCLUDE_FILE=$?
	if [[ $INCLUDE_FILE -eq '0' ]]; then
		echo "	Including: $file"
		cat $file >> $OUT_FILE;
		echo "" >> $OUT_FILE;
	else
		echo "	Excluding: $file"
	fi
done
