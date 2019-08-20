# bc-system-demo
Demonstration for BC system upgrade

## Installation and testing
Clone repo as is to any location. Ensure Python3 is on system path, and pip install all libraries listed as imports in bccmod/statemachine.py

add a folder and secrets/InitialStateConfig.ini into the base folder, and add a valid access key for the InitialState bucket we define, see here for reference:  https://github.com/initialstate/python_appender/blob/master/example_app/isstreamer.ini.example

python demo.py to start up. English voice functions won't work on non-windows machines yet. KH language will. 


