#!/bin/bash

INPUT_DIR=$1
ROOT_DIR=$2
shift 2
SYSTEM_TAGS="${@}"

FILES=`find $INPUT_DIR ! -name 'build' ! -name '*~' ! -path $INPUT_DIR ! -name build.sh | sort`

for file in $FILES; do
	FILE_NAME=`basename $file`
	FILE_TAGS=$(echo "$FILE_NAME" | grep -o -E '\([^\)]+\)' | sed -r 's/\((.+)\)/\1/')
	FILE_NAME_WITHOUT_TAGS=`$ROOT_DIR/tools/contains_tags.py $FILE_NAME $SYSTEM_TAGS`
	INCLUDE_FILE=$?
	if [[ $INCLUDE_FILE -eq '0' ]]; then
		echo "	Including: $file" 1>&2
		if [[ -d $file ]]; then
			if [ -f $file/build ]; then
				$file/build $file $ROOT_DIR $SYSTEM_TAGS
			else
				echo "		WARNING: No build file in: $file" 1>&2
			fi
		else
			cat $file
		fi
		echo ""
	else
		echo "	Excluding: $file" 1>&2
	fi
done
