#! /bin/bash


cd "$(git rev-parse --show-toplevel)"/data
pytest test.py
