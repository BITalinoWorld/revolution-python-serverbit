chdir "%~dp0"
taskkill /F /IM "python.exe" /T
"python_win64\python.exe" "ServerBIT.py"
