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
from bccmod.event import _event

class _station:

	pwd = os.path.dirname(__file__) # Gets absolute path to the directory that contains this file, not calling location.

	# TODO add config path and handle config file reading and writing, maybe implement using pickle for simplicity. or using scan codes - neater.

	def __init__(self):

		# self.storedEvents = []
		self.status = "GREEN" # This will be used for stack lights. 
		self.stackLight = "YELLOW" # When initialising
		self.updateStackLight()

		self.timer = _interactionTimer(self)
		self.sfx = _soundController(self)
		self.output = _outputManager(self)

		self.event = _event(self)

		self.name = self.output.getConfig('DEFAULT','name')

		self.output.terminalOutput("\n\nStation ~{}~ is now active\n\n".format(self.name),style="SUCCESS")

		self.updateStatus(self, "GREEN")

		# TODO - Allow for collecting config info from a specific file location, read it in line by line as now using the parse function. 

		# I think the first version of a dashboard would probably use this and trigger if a station is silent for too long etc. 

	def updateStatus(self, component, status):

		component.status=status

		# Check all stati and collate to inform station status

		stati = [self.status, self.timer.status, self.sfx.status, self.output.status]

		if 'RED' in stati:
			self.stackLight='RED'
			self.updateStackLight()
			return 1
		elif 'YELLOW' in stati:
			self.stackLight='YELLOW'
			self.updateStackLight()
			return 1
		else:
			self.stackLight='GREEN'
			self.updateStackLight()
			return 1

	def updateStackLight(self):

		# This will set the stack light colour based on self.stackLight
		print("Stack Light is now {}".format(self.stackLight))

		return 1

	def parse(self, textInput):

		textInput = textInput.lower()
		self.timer.registerActiveInput() # Let's the timer know that we just recieved input

		# Checks for valid data entry

		if(textInput.startswith('bc') and len(textInput)>2 and len(textInput)<12): # Then we have a bc number we should enter
			self.event.setBCC(textInput)
			self.sfx.announceOK()
			return 1

		if(textInput.startswith('op') and len(textInput)>2 and len(textInput)<5): # Then we have a op number we should enter
			self.event.setOpNum(textInput)
			self.sfx.announceOperationNumber(textInput)
			return 1

		if(textInput.startswith('20') and len(textInput)>8 and len(textInput)<11): # Then we have a employee number we should enter
			self.event.setEmpNum(textInput)
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
				self.event.setEventType("start1")
				self.sfx.announceOK()
				return 1

			if (textInput.find('fin1')!=-1): # Then we record a finish1 event
				self.event.setEventType("finish1")
				self.sfx.announceOK()
				return 1

			if (textInput.find('bgn2')!=-1): # Then we record a start2 event
				self.event.setEventType("start2")
				self.sfx.announceOK()
				return 1

			if (textInput.find('fin2')!=-1): # Then we record a finish2 event
				self.event.setEventType("finish2")
				self.sfx.announceOK()
				return 1

			if (textInput.find('ok')!=-1): # Then the user wants to commit data, we should check if it's ok
				self.event.setCommitted(1)

				if (not self.event.isComplete()):
					# Keep us uncommitted if there's not enough data yet
					self.event.setCommitted(0)
					# Get an event payload here and pass it to announce
					self.sfx.announceMissingInfo(self.BCC, self.empNum, self.opNum, self.eventType)
				
				self.event.showEvent()
				return 1

			if (textInput.find('clr')!=-1): # The user wants to clear everything
				self.event.clearValues()
				self.sfx.announceClearedAll()
				self.output.terminalOutput('Cleared all at user request', style='ALERT')
				return 1

		# Checks for valid parameter changes

		if(textInput.startswith('lang-') and len(textInput)>5 and len(textInput)<10): # Then we have a lanaguage change

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
			self.output.setConfig('DEFAULT','name',self.name)
			self.output.terminalOutput('New station name is: {}'.format(self.name), style='INFO')
			self.output.setDweetThingName(self.name) # Dweet names are automatically updated to match station names for now.
			self.sfx.announceOK()

			return 1

		if(textInput.startswith('loc-') and len(textInput)>4 and len(textInput)<15): # Then we have a location setting

			self.location = textInput.split('-')[1]
			self.output.setConfig('DEFAULT','location',self.location)
			self.output.terminalOutput('New station location is: {}'.format(self.location), style='INFO')
			self.sfx.announceOK()

			return 1 # Do this either way

		# Checks for valid scrap input

		if(textInput.startswith('scrp-') and len(textInput)>5 and len(textInput)<9): # Then we have a scrap input to process

			self.event.scrapInput(textInput)
			if not self.event.scrapValid():

				print('scrap cleared because invalid')
				# This automatically clears the scrap count
				# self.sfx.announceInvalidScrap() # Alert the user that scrap is invalid and tell them to do it again (or leave it blank)

			return 1 # Do this either way

		# Checks for valid control commands

		if(textInput.startswith('ctrl-') and len(textInput)>5 and len(textInput)<10): # Then we have a control function to run

			if (textInput.find('exit')!=-1): # Then we need to quit the application
				self.output.terminalOutput('Exit application', style='ALERT')
				self.sfx.announceOK()
				exit()
				return 1 # But it'll never get here lol

		self.output.terminalOutput('Unrecognised command',style='ALERT')

		# VOICE FEEDBACK NEEDED - yes.

		return 0

	def showEvent(self):

		self.output.terminalOutput('Employee {} reports {} for step {} on card {} - committed: {}'.format(self.empNum, self.eventType, self.opNum, self.BCC, self.committed),style='INFO')

	def isComplete(self):

		return self.event.isComplete()

	def clearCurrent(self):

		self.event.clearValues()

		self.timer.clear()

		self.output.terminalOutput("Last event has been cleared - ready for new event",style='INFO')
		
		return 1

	def writeEventToLocalFile(self):

		# Accept payload from event for filewrite func

		self.output.writeEventToLocalFile(self.event.getAsPayload())

		self.sfx.announceCompleteState() # TODO move this somewhere more sensible

		return 1

	def uploadEvent(self):

		# Accept payload from event for status funcs

		statusDweet = self.output.uploadEventToDweet(self.event.getAsPayload())

		statusIS = self.output.uploadEventToInitialState(self.event.getAsPayload())

		return (statusDweet and statusIS) # TODO modify since dweet is not as important as IS, nor as an API call to BC will be eventually.

		return 1

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
		self.event.clearValues()
		self.sfx.announceFreshStart()

	def startKeepAlive(self):

		self.timer.startKeepAlive()

   	# End class
