#!/bin/sh

if [ -z "$1" ]
  then /bin/ash 
else 
  exec /usr/bin/jsnapy "$@"
fi
