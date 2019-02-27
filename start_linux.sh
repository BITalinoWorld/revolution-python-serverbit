#!/bin/bash
cd "$( dirname "${BASH_SOURCE[0]}" )/"
pkill -f ServerBIT.py
python3 ServerBIT.py
