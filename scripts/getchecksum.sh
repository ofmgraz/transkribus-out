#!/bin/sh
# The script gets the checksums of the regular files in a given directory tree
# and saves them in a CSV file with their names and the timestamp

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
REG='\033[0m'
DATE=`date -Im`
OUTPUTFILE="checksums.csv"

# If first argument is -d, it does not overwrite the log file.
# Needed for recursive calls to explore subdirectories
if [ "$1" != "-d" ]; then
	echo > $OUTPUTFILE
else
	for arg do
		shift
		[ "$arg" = "-d" ] && continue
		set -- "$@" "$arg"
	done
fi

for file in $@; do
	# If it is a directory, the script calls itself
	if [ -d "$file" ]; then
		echo "[${YELLOW}--${REG}]\tEntering directory $file"
		eval "./$0 -d $file/*"
	# If it is a regular file, it gets the checksum
	elif [ -f "$file" ]; then
		echo "`cksum --untagged -a md5 $file|awk '{print $2","$1}'`,$DATE" >> $OUTPUTFILE
		echo "`cksum --untagged -a md5 $file|awk '{print $2","$1}'`,$DATE"
		echo "[${GREEN}OK${REG}]\t$file"
	# In case it is something else such as symlink or a device, the script ignores it
	else
		echo "[${RED}KO${REG}]\t${file}: Unrecognised file type"
	fi
done
