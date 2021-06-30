#!/bin/bash


if [[ $1 = '-s' ]]
then
	pip install -r resources/requirements.txt
	python3 python_scripts/db_create.py
fi

python3 python_scripts/db_update.py
python3 python_scripts/app.py

