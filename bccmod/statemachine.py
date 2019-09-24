# New automated BC system input using barcode scanner.
# (c) Leo Jofeh @ bespokh.com August 2019

# Handle dates and times

import datetime as dt
import time

# Handle OS, platform, config files

import os
import platform
import configparser

# Other related modules in bccmod

from bccmod.interactiontimer import _interactionTimer
from bccmod.soundcontroller import _soundController
from bccmod.outputmanager import _outputManager

class _station:

	pwd = os.path.dirname(__file__) # Gets absolute path to the directory that contains this file, not calling location.

	# TODO add config path and handle config file reading and writing, maybe implement using pickle for simplicity. or using scan codes - neater.

	def __init__(self):

		self.BCC = None
		self.opNum = None
		self.empNum = None
		self.eventType = None
		self.committed = 0
		self.storedEvents = []

		self.timer = _interactionTimer()
		self.sfx = _soundController()
		self.output = _outputManager()

		self.event = _event(self)

		self.name = "PACTICS_demo"

		self.output.terminalOutput("\n\nStation ~{}~ is now active\n\n".format(self.name),style="SUCCESS")

		# TODO - Allow for collecting config info from a specific file location, read it in line by line as now using the parse function. 

		# I think the first version of a dashboard would probably use this and trigger if a station is silent for too long etc. 

	def parse(self, textInput):

		textInput = textInput.lower()
		self.timer.registerActiveInput() # Let's the timer know that we just recieved input

		# Checks for valid data entry

		if(textInput.startswith('bc') and len(textInput)>2 and len(textInput)<12): # Then we have a bc number we should enter
			self.BCC = textInput
			self.sfx.announceOK()
			return 1

		if(textInput.startswith('op') and len(textInput)>2 and len(textInput)<5): # Then we have a op number we should enter
			self.opNum = textInput
			self.sfx.announceOperationNumber(self.opNum)
			return 1

		if(textInput.startswith('20') and len(textInput)>8 and len(textInput)<11): # Then we have a employee number we should enter
			self.empNum = textInput
			self.sfx.announceOK()
			return 1

		# Checks for valid actions

		if(textInput.startswith('act-') and len(textInput)>4 and len(textInput)<10): # Then we have an action to consider

			if(textInput.find('tgt')!=-1): # This is the practice target code, for helping people to practice scanning codes quickly
				self.sfx.announceOK()
				return 1

			if(textInput.find('rpt')!=-1): # Repeat the last announcement
				self.sfx.repeatLast()
				return 1

			if (textInput.find('bgn1')!=-1): # Then we record a start1 event
				self.eventType="start1"
				self.sfx.announceOK()
				return 1

			if (textInput.find('fin1')!=-1): # Then we record a finish1 event
				self.eventType="finish1"
				self.sfx.announceOK()
				return 1

			if (textInput.find('bgn2')!=-1): # Then we record a start2 event
				self.eventType="start2"
				self.sfx.announceOK()
				return 1

			if (textInput.find('fin2')!=-1): # Then we record a finish2 event
				self.eventType="finish2"
				self.sfx.announceOK()
				return 1

			if (textInput.find('ok')!=-1): # Then the user wants to commit data, we should check if it's ok
				self.committed=1
				if (not self.isComplete()):
					self.committed = 0 # Keep us uncommitted if there's not enough data yet
					self.sfx.announceMissingInfo(self.BCC, self.empNum, self.opNum, self.eventType)
				
				self.showEvent()
				return 1

			if (textInput.find('clr')!=-1): # The user wants to clear everything
				self.clearCurrent()
				self.sfx.announceClearedAll()
				self.output.terminalOutput('Cleared all at user request', style='ALERT')
				return 1

		# Checks for valid parameter changes

		if(textInput.startswith('prm-') and len(textInput)>4 and len(textInput)<10): # Then we have a parameter to consider

			if (textInput.find('kh')!=-1): # Then we change the language to KH
				self.sfx.lang="KH"
				self.sfx.announceOK()
				return 1

			if (textInput.find('en')!=-1): # Then we change the language to EN
				self.sfx.lang="EN"
				self.sfx.announceOK()
				return 1

		if(textInput.startswith('name-') and len(textInput)>5 and len(textInput)<20): # Then we have a renaming to perform

			self.name = textInput.split('-')[1]
			self.output.terminalOutput('New station name is: {}'.format(self.name), style='INFO')
			self.output.setDweetThingName(self.name)
			self.sfx.announceOK()

			return 1

		# Checks for valid control commands

		if(textInput.startswith('ctrl-') and len(textInput)>5 and len(textInput)<10): # Then we have a control function to run

			if (textInput.find('exit')!=-1): # Then we need to quit the application
				self.output.terminalOutput('Exit application', style='ALERT')
				self.sfx.announceOK()
				exit()
				return 1

		self.output.terminalOutput('Unrecognised command',style='ALERT')

		# VOICE FEEDBACK NEEDED??
		return 0

	def showEvent(self):

		self.output.terminalOutput('Employee {} reports {} for step {} on card {} - committed: {}'.format(self.empNum, self.eventType, self.opNum, self.BCC, self.committed),style='INFO')

	def isComplete(self):

		# Check if any field is filled in, and the timer is unstarted - then we should start a timer

		if ((self.BCC!=None or self.opNum!=None or self.empNum!=None or self.eventType!=None) and self.timer.isUnstarted()):
			self.timer.start()

		# Now we check if it's complete

		if (self.BCC!=None and self.opNum!=None and self.empNum!=None and self.eventType!=None and self.committed!=0):
			
			if (not self.timer.isUnstarted()): # Check we actually have a start time listed.
				self.timer.stop()
			else:
				self.output.terminalOutput("Complete with no timing available",style='ALERT')

			return 1
		else:
			return 0

	def clearCurrent(self):

		self.BCC = None
		self.opNum = None
		self.empNum = None
		self.eventType = None
		self.committed = 0

		self.timer.clear()

		self.output.terminalOutput("Last event has been cleared - ready for new event",style='INFO')
		
		return 1

	def writeEventToLocalFile(self):

		strTime = dt.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

		self.output.writeEventToLocalFile(self.BCC, self.empNum, self.opNum, self.eventType, strTime, self.timer.getTiming())

		self.sfx.announceCompleteState() # TODO move this somewhere more sensible

		return 1

	def uploadEvent(self):

		strTime = dt.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
		intTime = str(round(self.timer.getTiming()))

		statusDweet = self.output.uploadEventToDweet(self.BCC, self.empNum, self.opNum, self.eventType, strTime, intTime)

		statusIS = self.output.uploadEventToInitialState(self.BCC, self.empNum, self.opNum, self.eventType, strTime, intTime)

		return (statusDweet and statusIS)

	def storeForLater(self):
		self.output.terminalOutput("Storing for later",style='INFO')
		# TODO help this class remember events that failed to upload because of internet connection.
		# self.storedEvents.append(info)
		return 1

	def catchupUploads(self):
		# TODO help this class re-attempt failed uploads due to internet connectivity.

		# Think about what mechanism this might use to store and systematically check that things worked (or not)
		return 1

	def freshStart(self):

		self.timer.clear()

		self.sfx.announceFreshStart()

	def startKeepAlive(self):

		self.timer.startKeepAlive()

   	# End class






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

		self.scrapValue = 0

		# Other variables etc go here.

	def setBCC(self, incoming):

		if (not isinstance(self.BCC, type(None))) and self.BCC!=incoming:
			self.station.output.terminalOutput('Overwriting BC card number',style="INFO")

		self.BCC=incoming

	def setOpNum(self, incoming):

		if (not isinstance(self.opNum, type(None))) and self.opNum!=incoming:
			self.station.output.terminalOutput('Overwriting operation number',style="INFO")

		self.opNum=incoming

	def setEmpNum(self, incoming):

		if (not isinstance(self.empNum, type(None))) and self.empNum!=incoming:
			self.station.output.terminalOutput('Overwriting employee number',style="INFO")

		self.empNum=incoming

	def setEventType(self, incoming):

		if (not isinstance(self.eventType, type(None))) and self.eventType!=incoming:
			self.station.output.terminalOutput('Overwriting event type',style="INFO")

		self.eventType=incoming

	def getAsPayload(self):

		# This should return the current event as a well-formed dictionary payload suitable for dweet or IS, or another service.

		return {}

