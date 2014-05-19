#!/bin/bash

ROOT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SYSTEM_TAGS=( `cat ~/.dotfiles.conf 2>/dev/null ` )
BUILD_DIR=$ROOT_PATH/build

rm -fr $BUILD_DIR
mkdir $BUILD_DIR

for dir in $ROOT_PATH/*; do
	NAME=`basename $dir`
	NAME_WITHOUT_TAGS=`$ROOT_PATH/tools/contains_tags.py $NAME $SYSTEM_TAGS`
	INCLUDE_DIR=$?
	if [[ $INCLUDE_DIR -eq '0' ]]; then
		if [ -f $dir/build ]; then
			echo "Building $dir"
			$dir/build $dir $NAME_WITHOUT_TAGS $BUILD_DIR $ROOT_PATH ${SYSTEM_TAGS[@]}
		fi
	else
		echo "Excluding: $dir"
	fi

done


for file in `find $BUILD_DIR -type f -name '*.symlink'`; do
	NAME=`basename $file .symlink`
	CURRENT_SYMLINK=`readlink ~/$NAME`
	if [ "$CURRENT_SYMLINK" == "$file" ]; then
		echo "Link already exists for $NAME"
	else
		echo "Linking $NAME"
		ln -bf --symbolic $file ~/$NAME;
	fi
done

