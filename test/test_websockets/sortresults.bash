#! /bin/bash

cat *.log* > ./LOG.log
awk -F":" '{print $3}' ./LOG.log | sed 's/,/\./' | sort -n
rm *.log*
