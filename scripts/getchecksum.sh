#!/bin/sh
# The script gets the checksums of the regular files in a given directory tree
# and saves them in a CSV file with their names and the timestamp

# For a visual info output
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
	for ARG do
		shift
		[ ${ARG} = "-d" ] && continue
		set -- "$@" "${ARG}"
	done
fi

for FILE in $@; do
	# If it is a directory, the script calls itself
	if [ -d ${FILE} ]; then
		echo "[${YELLOW}--${REG}]\tEntering directory ${FILE}"
		eval "./$0 -d ${FILE}/*"
	# If it is a regular file, it gets the checksum
	elif [ -f "$FILE" ]; then
		echo "`cksum --untagged -a md5 ${FILE}|awk '{print $2","$1}'`,${DATE}" |tee -a ${OUTPUTFILE}
		echo "[${GREEN}OK${REG}]\t${FILE}"
	# In case it is something else such as symlink or a device, the script ignores it
	else
		echo "[${RED}KO${REG}]\t${FILE}: Unrecognised file type"
	fi
done
