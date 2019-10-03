# event.py
# (c) Leo Jofeh @ bespokh.com August 2019
# Defines an event class for interactions with staff logging details of operations

# Imports

# Handle dates and times

import datetime as dt
import time

# Handle OS, platform, config files

import os
import platform
import configparser

class _event:

	# This class must keep track of all data for an event, and provide some useful functions

	def __init__(self, station):

		self.station = station

		self.clearValues()

	def clearValues(self):

		self.BCC = None
		self.opNum = None
		self.empNum = None
		self.eventType = None
		self.committed = 0
		self.interactionTime = 0
		self.commitTime = None

		self.scrapValue = '0' # Cheat by using an implicit cast from string to check whether it is valid or not

		# Other variables etc go here.

	def isComplete(self):

		# TODO - ensure that scrap value is ZERO if this is a begin1 or begin2 event - scrap counts are only valid on fin1 and fin2 events.

		complete = (self.BCC!=None and self.opNum!=None and self.empNum!=None and self.eventType!=None and self.committed!=0)
		if complete:
			self.station.timer.stop()
			self.interactionTime = str(round(self.station.timer.getTiming()))
			self.commitTime = dt.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

		return complete

	def showEvent(self):

		scrpVal = float(self.scrapValue)

		self.station.output.terminalOutput('Employee {} reports {} for step {} on card {} with {} scrap - committed: {}'.format(self.empNum, self.eventType, self.opNum, self.BCC, scrpVal, self.committed),style='INFO')

	def hasAnything(self):

		# Check whether any BC card fields have been filled in

		return (self.BCC!=None or self.opNum!=None or self.empNum!=None or self.eventType!=None)

	def setBCC(self, incoming):

		if (not isinstance(self.BCC, type(None))) and self.BCC!=incoming:
			self.station.output.terminalOutput('Overwriting BC card number',style="INFO")

		self.BCC=incoming
		self.eventDataAhoy()

	def setOpNum(self, incoming):

		if (not isinstance(self.opNum, type(None))) and self.opNum!=incoming:
			self.station.output.terminalOutput('Overwriting operation number',style="INFO")

		self.opNum=incoming
		self.eventDataAhoy()

	def setEmpNum(self, incoming):

		if (not isinstance(self.empNum, type(None))) and self.empNum!=incoming:
			self.station.output.terminalOutput('Overwriting employee number',style="INFO")

		self.empNum=incoming
		self.eventDataAhoy()

	def setEventType(self, incoming):

		if (not isinstance(self.eventType, type(None))) and self.eventType!=incoming:
			self.station.output.terminalOutput('Overwriting event type',style="INFO")

		self.eventType=incoming
		self.eventDataAhoy()

	def setCommitted(self, incoming):

		self.committed = incoming
		self.eventDataAhoy()

	def scrapInput(self, incoming):

		# This function accepts numbers and handles the internal representation of scrap.
		# Try to parse it as an integer first. If that fails, then check for the text meaning.

		incoming=incoming.split('-')[1] # This is the pure value component
		self.eventDataAhoy()

		try:

			temp=int(incoming) # If this is successful then it's reliably an integer

			self.scrapValue=self.scrapValue+incoming # Append as string representation of number

		except:

			if incoming=='pt':
				self.scrapValue=self.scrapValue+'.'

			if incoming=='clr':
				self.scrapValue='0'

		return 1

	def scrapValid(self):

		try:

			val = float(self.scrapValue)
			# TODO Do a sanity check on the value here
			return True

		except:

			self.scrapValue='0' # Clear it # Either here or in the calling bloack, announce the problem nicely.
			return False

	def eventDataAhoy(self):

		# Start the interaction timer if we are receiving data and it hasn't already been started
		if self.station.timer.isUnstarted():
			self.station.timer.start()

	def getAsPayload(self):

		# This should return the current event as a well-formed dictionary payload suitable for dweet or IS, or another service.

		payload = {
		"stationName" : self.station.name
		"stationLocation" : self.station.location
		"BCC" : self.BCC,
		"opNum" : self.opNum,
		"empNum" : self.empNum,
		"eventType" : self.eventType,
		"time" : self.commitTime,
		"interactionTime" : self.interactionTime,
		"scrap" : str(float(self.scrapValue))
		}

		return payload
