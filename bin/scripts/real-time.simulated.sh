#!/bin/bash

USAGE='my_script <folder1> <folder-realtime> <sleep_time (default 2)>'

if [[ $# < 2 ]]; then
	echo $USAGE
	exit
fi

folder1=$1
folder_realtime=$2
sleep_time=$3

sleep_time=$(( $sleep_time + 0 ))
folder1=$folder1"/*"

i=0
for file in $folder1; do
filename=`basename $file`;

cp $file $folder_realtime/$filename;
i=$(( $i + 1)); 
sleep $sleep_time;

echo "$i files tranfer: $filename"
done

