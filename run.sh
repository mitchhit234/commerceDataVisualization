#!/bin/bash

#run with the -u tag if you do not want 
#to update your transaciton json with plaid
if [[ $1 != '-u' ]]; 
then
  python3 python_scripts/server.py
fi

python3 python_scripts/app.py
