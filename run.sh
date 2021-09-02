#!/bin/bash

#run with the -u tag if you do not want 
#to update your transaciton json with plaid
if [[ $1 = '-u' || $2 = '-u' ]]; 
then
  #run with the -s tag if you want
  #the applications to run without automatically
  #opening the web browsers (say if you want to access
  #application on a seperate computer over the network)
  if [[ $1 = '-s' || $2 = '-s' ]];
  then
    python3 python_scripts/app.py -s
  else
    python3 python_scripts/app.py
  fi
else
  if [[ $1 = '-s' || $2 = '-s' ]];
  then
    python3 python_scripts/server.py -s
    python3 python_scripts/app.py -s
  else
    python3 python_scripts/server.py
    python3 python_scripts/app.py
  fi
fi