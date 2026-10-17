#!/bin/bash

function Mark {
file=$1
text=$2
convert "$file" -fill grey -pointsize 20 -gravity NorthWest -draw "text 20,20 '$text'" -gravity SouthWest -draw "text 20,20 '$text'" -gravity SouthEast -draw "text 20,20 '$text'" "$file"
}

cacheFilename="watered_files.txt"
if [ ! -f "$cacheFilename" ]
then
touch "$cacheFilename"
fi
cache=$(cat "$cacheFilename")
for file in -. *
do
if grep -q "$file" <<< "$cache"
then
echo "$file has been watered"
else
echo "processing $file"
Mark "$file" "newbe.hagicode.com"
echo "$file" >> "$cacheFilename"
echo "processed $file"
fi
done
