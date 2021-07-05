#!/bin/bash

#pass -s argument for first time setup
#assumes you have python3 and pip installed
if [[ $1 = '-s' ]]
then
	python3 -m pip install -r resources/requirements.txt
	python3 python_scripts/db_create.py
fi

python3 python_scripts/app.py

