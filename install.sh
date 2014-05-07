#!/bin/bash

ROOT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

BUILD_DIR=$ROOT_PATH/build

rm -fr $BUILD_DIR
mkdir $BUILD_DIR

for dir in $ROOT_PATH/*; do
	if [ -f $dir/build.sh ]; then
		echo "Building $dir"
		$dir/build.sh $dir $BUILD_DIR
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

