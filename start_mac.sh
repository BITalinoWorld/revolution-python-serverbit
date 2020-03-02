#!/bin/bash
cd "$( dirname "${BASH_SOURCE[0]}" )/"
pkill -f Python
python ServerBIT.py &
python osx_statusbar_app.py
