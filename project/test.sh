#! /bin/bash

if [ "$current_dir" == "project" ]
then
    # if current directory is 'project', go to '../data'
    cd ../data
else
    # if not, go to './data'
    cd ./data
pytest test.py
