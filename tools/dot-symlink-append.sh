#!/bin/bash

INPUT_DIR=$1
OUTPUT_DIR=$2
shift 2
SYSTEM_TAGS="${@}"

NAME=`basename $INPUT_DIR`
OUT_FILE=$OUTPUT_DIR/.$NAME.symlink

FILES=`find $INPUT_DIR -type f ! -name 'build' ! -name '*~' | sort`

for file in $FILES; do
	FILE_NAME=`basename $file`
	FILE_TAGS=$(echo "$FILE_NAME" | grep -o -E '\([^\)]+\)' | sed -r 's/\((.+)\)/\1/')
	INCLUDE_FILE=1
	if [[ -z $FILE_TAGS  ]]; then
		INCLUDE_FILE=1
	else
		for TAG in $FILE_TAGS; do
			TAG_FOUND=0
			for SYSTEM_TAG in $SYSTEM_TAGS; do
				if [[ $SYSTEM_TAG == $TAG ]]; then
					TAG_FOUND=1
				fi
			done
			if [[ $TAG_FOUND -eq '0' ]]; then
				INCLUDE_FILE=0
			fi
		done
	fi
	if [[ $INCLUDE_FILE -eq '1' ]]; then
		echo "	Including: $file"
		cat $file >> $OUT_FILE;
	else
		echo "	Excluding: $file"
	fi
done
