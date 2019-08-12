# demo.py
# demonstration/hacky first attempt at new automated BC system input using barcode scanner.
# (c) Leo Jofeh @ bespokh.com July 2019

# Important TODO: add support for config via scanned codes, and persistence of config info in files.

# imports

# Class defs

from bccmod.statemachine import _state

# Handle dates and times

import datetime as dt

# Handle OS

import os

# MAGIC NUMBERS

# Main control flow

def go():
	station = _state()
	running = True

	while (running):
		station.playVoice("Ready for new operation!")
		while (not station.isComplete()): # This ends when all fields are valid and the user has committed.
			latest = input("Scan something: ") # should always end with a carriage return
			station.parse(latest)
			continue
		station.playVoice("Recording operation data.")
		# Get the date and time
		strTime = dt.datetime.now().strftime("%d/%m/%Y-%H:%M:%S") # This is system local time string right now
		print("Got time: ",strTime)
		writeOK = station.writeEventToLocalFile(strTime)
		uploadOK = station.uploadEvent(strTime)
		if (not writeOK):
			station.storeForLater()
			station.playVoice("Failed to write.")
		station.clearCurrent()
		station.playVoice("Success.")
		continue

try:
    go()
except KeyboardInterrupt:
    print('\n\nKeyboard exception received. Exiting.')
    exit()

# That's all folks!