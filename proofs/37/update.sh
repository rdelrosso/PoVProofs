#!/bin/sh
# created 01/04/2022 - steve.walsh
#
if [ $# -ne 2 ]; then
  echo usage\: `basename $0` \<QUERY ENDPOINT\> \<TYPEAHEAD URL\>
  exit
fi
tmp=/tmp/`basename $0`-tmp.out
file=realm-fts-pov/hosting/files/search.html
rm -f $tmp
mv $file $file.orig
cat $file.orig | sed "s#<PASTE QUERY ENDPOINT URL HERE>#$1#"> $tmp
cat $tmp | sed "s#<PASTE TYPEAHEAD URL HERE>#$2#" > $file
