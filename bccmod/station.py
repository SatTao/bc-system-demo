# New automated BC system input using barcode scanner.
# (c) Leo Jofeh @ bespokh.com August 2019

# Handle dates and times

import datetime as dt
import time

# Handle OS, platform, config files

import os
import platform
import configparser

# pattern matching for input

import re

# Traffic lights - PiStop - only works on rpi

from gpiozero import TrafficLights

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
		try:
			self.stack=TrafficLights(2,3,4) # Set up the hardware forthe traffic lights
			self.stacklightsAvailable=True
		except:
			print("Skipping stacklights - unsupported on this OS")
			self.stacklightsAvailable=False
		self.updateStackLight()

		self.timer = _interactionTimer(self)
		self.output = _outputManager(self)
		self.sfx = _soundController(self)

		self.event = _event(self)

		self.name = self.output.getConfig('DEFAULT','name')
		self.location = self.output.getConfig('DEFAULT','location')
		self.version='Apathetic Aunt' # Taken from https://www.michaelfogleman.com/phrases/

		self.recognised={ # regexes which differentiate the recognised codes exactly
		'bcc' : re.compile(r'^bc\d+$'), # https://pythex.org/?regex=%5Ebc%5Cd%2B%24&test_string=bc365939269%0Abcs%0A5429bc97870%0ABC111%0Abcb5689&ignorecase=0&multiline=1&dotall=0&verbose=0
		'operation' : re.compile(r'^op\d+$'), # https://pythex.org/?regex=%5Eop%5Cd%2B%24&test_string=op90%0Aopop%0A78o9%0Ao3p4p5o%0A247&ignorecase=1&multiline=1&dotall=0&verbose=0
		'employee' : re.compile(r'^20\d{2}(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[1-9]|3[0-1])\d+$'), # https://pythex.org/?regex=%5E20%5Cd%7B2%7D(0%5B1-9%5D%7C1%5B0-2%5D)(0%5B1-9%5D%7C1%5Cd)%5Cd%2B%24&test_string=2019010203%0A2010030410%0A2010011209%0A200464531%0A19990203%0Aemp987902u2&ignorecase=1&multiline=1&dotall=0&verbose=0
		'combo' : re.compile(r'^cmb-(?P<bcc>bc\d+)\|(?P<op>op\d+)\|act-(?P<act>\w+)$'), # https://pythex.org/?regex=%5Ecmb-(%3FP%3Cbcc%3Ebc%5Cd%2B)%5C%7C(%3FP%3Cop%3Eop%5Cd%2B)%5C%7C(%3FP%3Cact%3Eact-%5Cw%2B)&test_string=cmb-bc239587485%7Cop78%7Cact-bgn1&ignorecase=1&multiline=1&dotall=0&verbose=0
		'actprefix' : re.compile(r'^act-\w+$'), # https://pythex.org/?regex=%5Eact-%5Cw%2B%24&test_string=actact%0Aact-ok%0Aact-35294-%0Aact%0Atca34&ignorecase=1&multiline=1&dotall=0&verbose=0
		'ctrlprefix' : re.compile(r'^ctrl-\w+$'), # https://pythex.org/?regex=%5Ectrl-%5Cw%2B%24&test_string=ctrl-exit%0Actrlctrl%0Actrl90%0Actrl-act-&ignorecase=1&multiline=1&dotall=0&verbose=0
		'scrapprefix' : re.compile(r'^scrp-\w+$'),
		'nameprefix' : re.compile(r'^name-\w+$'),
		'locationprefix' : re.compile(r'^loc-\w+$'),
		'langprefix' : re.compile(r'^lang-\w+$'),
		}

		self.output.terminalOutput("\n\nStation ~{}~ is now active\n\n".format(self.name),style="SUCCESS")

		self.updateStatus(self, "GREEN")

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

		if self.stacklightsAvailable:

			self.stack.green.off()
			self.stack.amber.off()
			self.stack.red.off()

			if self.stackLight=="GREEN":
				self.stack.green.on()
			if self.stackLight=="YELLOW":
				self.stack.amber.on()
			if self.stackLight=="RED":
				self.stack.red.on()

			print("Stack Light is now {}".format(self.stackLight))

			return 1
		return 0

	def parse(self, textInput):

		textInput = textInput.lower()
		self.timer.registerActiveInput() # Let's the timer know that we just recieved input

		# Checks for valid data entry by matching to a compiled regex 

		if self.recognised['bcc'].match(textInput): 
			self.event.setBCC(textInput)
			self.sfx.announceOK()
			return 1

		if self.recognised['operation'].match(textInput):
			self.event.setOpNum(textInput)
			self.sfx.announceOperationNumber(textInput)
			return 1

		if self.recognised['employee'].match(textInput):
			self.event.setEmpNum(textInput)
			self.sfx.announceOK()
			return 1

		if self.recognised['combo'].match(textInput): # Then we have a new combo code to consider. (Change to := in Python3.8+) TODO change to minimised code

			match = self.recognised['combo'].match(textInput)
			self.event.setBCC(match.group('bcc')) # The match object automatically scrapes the relevant data to its groups
			self.event.setOpNum(match.group('op'))
			self.event.setEventType(match.group('act'))
			# We should support announcing the full info here, like "starting operation 80" or "finishing operation 45 for the second time" TODO!
			self.sfx.announceOK()

			return 1

		# Checks for valid actions

		if self.recognised['actprefix'].match(textInput): # Then we have an action to consider

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
					self.sfx.announceMissingInfo(self.event.getAsPayload()) # TODO change to payload
				
				self.event.showEvent()
				return 1

			if (textInput.find('clr')!=-1): # The user wants to clear everything
				self.event.clearValues()
				self.sfx.announceClearedAll()
				self.output.terminalOutput('Cleared all at user request', style='ALERT')
				return 1

		# Checks for valid parameter changes

		if self.recognised['langprefix'].match(textInput): # Then we have a lanaguage change

			if (textInput.find('kh')!=-1): # Then we change the language to KH
				self.sfx.lang="KH"
				self.sfx.announceOK()
				return 1

			if (textInput.find('en')!=-1): # Then we change the language to EN
				self.sfx.lang="EN"
				self.sfx.announceOK()
				return 1

		if self.recognised['nameprefix'].match(textInput): # Then we have a renaming to perform

			self.name = textInput.split('-')[1]
			self.output.setConfig('DEFAULT','name',self.name)
			self.output.terminalOutput('New station name is: {}'.format(self.name), style='INFO')
			self.output.setDweetThingName(self.name) # Dweet names are automatically updated to match station names for now.
			self.sfx.announceOK()

			return 1

		if self.recognised['locationprefix'].match(textInput): # Then we have a location setting

			self.location = textInput.split('-')[1]
			self.output.setConfig('DEFAULT','location',self.location)
			self.output.terminalOutput('New station location is: {}'.format(self.location), style='INFO')
			self.sfx.announceOK()

			return 1 # Do this either way

		# Checks for valid scrap input

		if self.recognised['scrapprefix'].match(textInput): # Then we have a scrap input to process

			self.event.scrapInput(textInput)
			if not self.event.scrapValid():

				print('scrap cleared because invalid')
				# This automatically clears the scrap count
				# self.sfx.announceInvalidScrap() # Alert the user that scrap is invalid and tell them to do it again (or leave it blank)

			return 1 # Do this either way

		# Checks for valid control commands

		if self.recognised['ctrlprefix'].match(textInput): # Then we have a control function to run

			if (textInput.find('exit')!=-1): # Then we need to quit the application
				self.output.terminalOutput('Exit application', style='ALERT')
				self.sfx.announceOK()
				exit()
				return 1 # But it'll never get here lol

		self.output.terminalOutput('Unrecognised command',style='ALERT')

		# VOICE FEEDBACK NEEDED - yes.

		return 0

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
		self.output.writeXML(self.event.getAsPayload())

		self.sfx.announceCompleteState() # TODO move this somewhere more sensible

		return 1

	def uploadEvent(self):

		# Accept payload from event for status funcs

		self.updateStatus(self, "YELLOW")

		statusDweet = self.output.uploadEventToDweet(self.event.getAsPayload())

		statusIS = self.output.uploadEventToInitialState(self.event.getAsPayload())

		statusBC = self.output.writeToBCC(self.event.getAsPayload())

		self.updateStatus(self, "GREEN")

		return (statusDweet and statusIS and statusBC) # TODO modify since dweet is not as important as IS, nor as an API call to BC will be eventually.

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
