#!/bin/bash
# $1 could be --dry
if [[ $1 == "" ]]
then
    FLAG=""
else 
    FLAG=$1
fi

#DRY_FLAG=$FLAG
#echo $DRY_FLAG

DRY_FLAG=$FLAG docker-compose up single_run
