#!/bin/sh

if [ -z "$1" ]
  then /bin/ash 

else 
  echo $@
  /usr/bin/jsnapy "$@"

fi
