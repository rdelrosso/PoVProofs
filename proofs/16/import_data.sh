# SA-POV-REPORTING Load Data Script
# Maintainer: gary.taylor@mongodb.com
# Version 1: 10 Feb 2019

echo
echo "Current Working Directory [ `pwd` ]"
source ./.atlas_env

echo
echo "Loading Airline Performance Data ..."
echo
echo "Connecting to [ ${MONGO_IMPORT_HOST} ]"

#
# Process the Airline Performance Data Files (CSV format)
#

COUNTER=0

for f in PERFORMANCE_DATA/*.gz
do 
        if [ "$COUNTER" -eq "0" ] ; then		# On processing very first file, drop the database if it exists
		COUNTER=$((COUNTER + 1))
		echo
		echo "FILE ${COUNTER}:[ $f ]"
		echo
		gunzip -c ${f} | tail -n +2 | \
			mongoimport \
			--host $MONGO_IMPORT_HOST \
			--ssl \
			--username $USER \
			--password $PASS \
			--authenticationDatabase admin \
			-j 4 \
			-d airlines \
			-c on_time_perf  \
			--drop \
			--type csv \
			--columnsHaveTypes \
			--fieldFile PERFORMANCE_DATA/on_time_perf_fields.fld
	else						# Not the first file being processed, do NOT drop the database
		COUNTER=$((COUNTER + 1))
		echo
		echo "FILE ${COUNTER}:[ $f ]"
		echo
		gunzip -c ${f} | tail -n +2 | \
			mongoimport \
			--host $MONGO_IMPORT_HOST \
			--ssl \
			--username $USER \
			--password $PASS \
			--authenticationDatabase admin \
			-j 4 \
			-d airlines \
			-c on_time_perf  \
			--type csv \
			--columnsHaveTypes \
			--fieldFile PERFORMANCE_DATA/on_time_perf_fields.fld
	fi
done

echo
echo "Processed ${COUNTER} Airline Performance Data files!"
echo

echo "Creating indexes ..."

mongo "mongodb+srv://${MONGO_SHELL_HOST}" --username $USER --password $PASS < ./createIndexes.js

echo "Finished processing!"
echo
