#!/bin/bash
cd "$( dirname "${BASH_SOURCE[0]}" )/"
pkill -f Python
python3 ServerBIT.py &
python3 osx_statusbar_app.py
