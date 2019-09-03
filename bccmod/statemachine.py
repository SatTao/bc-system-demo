# demonstration/hacky first attempt at new automated BC system input using barcode scanner.
# (c) Leo Jofeh @ bespokh.com August 2019

# Handle sound effects and t2v 

# Handle https

import requests as r

# Initial State streaming

from ISStreamer import Streamer

# Handle dates and times

import datetime as dt
import time

# Handle OS

import os

# Handle random string generation

import random
import string

# Used in number announcements

import math

# Other related modules in bccmod

from bccmod.interactiontimer import _interactionTimer
from bccmod.soundcontroller import _soundController

class _state:

	pwd = os.path.dirname(__file__) # Gets absolute path to the directory that contains this file, not calling location.
	thingName = "PACTICS_demo" # reference for dweet
	dataEndpoint = "https://www.dweet.io/dweet/for/" + thingName # This will move to __init__() for multiple instances, with names from config barcode.
	writePath = os.path.join(pwd,'../output/')
	configPath = os.path.join(pwd,'../secrets/')
	# TODO add config path and handle config file reading and writing, maybe implement using pickle for simplicity. or using scan codes - neater.


	def __init__(self):

		self.BCC = None
		self.opNum = None
		self.empNum = None
		self.eventType = None
		self.committed = 0
		self.storedEvents = []

		self.timer = _interactionTimer()
		self.sfx = _soundController(_state.pwd)

		self.mode = "AUTO"
		self.name = "default"

		self.uniqueString = self.createRandomString()
		self.outputFilename = ''.join([_state.writePath, dt.datetime.now().strftime("%Y-%m-%d_"), self.uniqueString, ".csv"])

		print("Output will be written to", self.outputFilename)
		print("Realtime data will be streamed to https://www.dweet.io/follow/" + _state.thingName)

		# TODO - Allow for collecting config info from a specific file location, read it in line by line as now using the parse function. 
		# Might consider making a special code to allow to change the name of the device and it will update its own config file to match when changed that way.
		# Once implemented we should also send our name to dweet so we can see what data is from where, and check on downtime etc.

		# I think the first version of a dashboard would probably use this and trigger if a station is silent for too long etc. 

		self.prepLocalFile()

		conf = ''.join([_state.configPath,"InitialStateConfig.ini"])
		self.stream = Streamer.Streamer(bucket_key="M5LW9T38AJ4T", bucket_name="pacticstester", debug_level=1, ini_file_location=conf)

	def createRandomString(self,length=6):

		random.seed()
		lettersAndDigits = string.ascii_letters + string.digits
		return ''.join(random.choice(lettersAndDigits) for i in range(length))

	def parse(self, textInput):

		textInput = textInput.lower()

		# Check for mode changes

		if(textInput.startswith('mode-') and len(textInput)>5 and len(textInput)<10): # Then we have a mode change to consider

			if (textInput.find('auto')!=-1):
				self.mode = 'AUTO'
				return 1
			if (textInput.find('prm')!=-1):
				self.mode = 'PRM'
				return 1

		# Checks for valid data entry and mode changes and actions in auto mode

		if (self.mode=="AUTO"):

			# Checks for valid data in AUTO mode

			if self.timer.isUnstarted(): # Then this is the first parse of an interaction - set a timer
				self.timer.start()

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

			# Checks for valid actions in AUTO mode

			if(textInput.startswith('act-') and len(textInput)>4 and len(textInput)<10): # Then we have an action to consider

				if(textInput.find('tgt')!=-1): # This is the practice target code, for helping people to practice scanning codes quickly
					self.sfx.announceOK()
					return 1

				if (textInput.find('bgn1')!=-1): # Then we record a start event
					self.eventType="start1"
					self.sfx.announceOK()
					return 1

				if (textInput.find('fin1')!=-1): # Then we record a start event
					self.eventType="finish1"
					self.sfx.announceOK()
					return 1

				if (textInput.find('bgn2')!=-1): # Then we record a start event
					self.eventType="start2"
					self.sfx.announceOK()
					return 1

				if (textInput.find('fin2')!=-1): # Then we record a start event
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
					print("Cleared all at user request")
					return 1

			print("Unrecognised command in AUTO mode") # Default if we don't understand any command here

			# VOICE FEEDBACK NEEDED
			return 0

		# Checks for valid data entry and mode changes and actions in parameter mode

		if (self.mode=="PRM"):

			self.timer.clear() # Shouldn't record time spent on these interactions

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
				print(self.name)
				self.sfx.announceOK()

				return 1

		print("Unrecognised mode")

		# VOICE FEEDBACK NEEDED
		return 0

	def showEvent(self):

		print(self.BCC, self.opNum, self.empNum, self.eventType, self.committed)

	def isComplete(self):

		if (self.BCC!=None and self.opNum!=None and self.empNum!=None and self.eventType!=None and self.committed!=0):
			
			if (not self.timer.isUnstarted()): # Check we actually have a start time listed.
				self.timer.stop()
				print("This event is complete in", str(round(self.timer.getTiming())), 'seconds')
			else:
				print("Complete with no timing available")

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

		print("Last event has been cleared - ready for new event")

		# VOICE FEEDBACK NEEDED
		
		return 1

	def prepLocalFile(self):

		f = open(self.outputFilename, "w")
		f.write(', '.join(["BCC", "EMP", "OP", "EVENT", "TIME", ("PTIME" + '\n')])) # comma separated values and builtin newline
		f.close()

		return 1

	def writeEventToLocalFile(self):

		# To do - think about modifying the file layout to more closely mirror existing BCC reports, so the event type field now dictates position in the row rather than being an entry of itself.

		strTime = dt.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
		print("Got time: ",strTime)

		f = open(self.outputFilename, "a")
		f.write(', '.join([self.BCC, self.empNum, self.opNum, self.eventType, strTime, (str(self.timer.getTiming()) + '\n')])) # comma separated values and builtin newline
		f.close()

		self.sfx.announceCompleteState()

		return 1

	def postIntitialState(self): # TODO implement logging to initial state service.

		payload = {
			"BCC" : self.BCC,
			"opNum" : self.opNum,
			"empNum" : self.empNum,
			"action" : self.eventType,
			"interactionTime" : str(round(self.timer.getTiming()))
			}

		self.stream.log_object(payload, key_prefix="")
		self.stream.flush()

		return 1

	def uploadEvent(self):

		# Package all data as a POST form

		strTime = dt.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

		payload = {
		"BCC" : self.BCC,
		"opNum" : self.opNum,
		"empNum" : self.empNum,
		"action" : self.eventType,
		"time" : strTime,
		"interactionTime" : str(round(self.timer.getTiming()))
		}

		# Post it and check the response, return 0 if bad response or timeout
		print("Attempting to POST")
		try:
			response = r.post(_state.dataEndpoint,data=payload, timeout=5)
			response.raise_for_status()
		except r.exceptions.HTTPError as errh:
			print ("Http Error:",errh)
			return 0
		except r.exceptions.ConnectionError as errc:
			print ("Error Connecting:",errc)
			return 0
		except r.exceptions.Timeout as errt:
			print ("Timeout Error:",errt)
			return 0
		except r.exceptions.RequestException as err:
			print ("Oops: Something Else",err)
			return 0

		print("Good POST to dweet for", _state.thingName)
		return 1 

		# TODO occasionally or if the last upload worked then retry anything in storedEvents

	def storeForLater(self):
		print ("Storing for later")
		# TODO help this class remember events that failed to upload because of internet connection.
		# self.storedEvents.append(info)
		return 1

	def catchupUploads(self):
		# TODO help this class re-attempt failed uploads due to internet connectivity.
		return 1

	def freshStart(self):

		self.timer.clear()

		self.sfx.announceFreshStart()


	# TODO consider adding a file handling class and a realtime data handling class so these functions all look cleaner.

   	# End class