#!/bin/sh

if [ -z "$1" ]
  then /bin/ash 
else 
  /usr/bin/jsnapy "$@"
fi
