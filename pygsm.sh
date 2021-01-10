#!/bin/bash
#
# Description:
# Open GSM GUI
# Param: Remote IP address
#
# Use batch file with SFTP shell script without prompting password
# using SFTP authorized_keys
#
# Usage: 
#   Connect: sh pygsm.sh <IP_Address>
#   Example : sh pygsm.sh 127.0.0.1
#
##################################################################
if [ $# -eq 0 ]
  then
    echo 'Usage: sh pysidegsm.sh <IP_Address>'
fi

if [ $# -gt 0 ]
  then
    python3 pysidegsm.py $@
fi