#!/bin/bash

if [ $# -ne 0 ]; then
    dt="$1"
else
    dt=`date +%Y%m%d`
fi

conf=../conf/conf.cfg

python run.py -t run -c ${conf} -d ${dt}