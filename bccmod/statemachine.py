# demonstration/hacky first attempt at new automated BC system input using barcode scanner.
# (c) Leo Jofeh @ bespokh.com August 2019

# Handle sound effects and t2v 

import win32com.client as wincl # modify for other platforms

import playsound as ps # should be platform agnostic

# Handle https

import requests as r

# Handle dates and times

import datetime as dt
import time

# Handle OS

import os

# Handle random string generation

import random
import string

class _state:

	thingName = "PACTICS_demo" # reference for dweet
	dataEndpoint = "https://www.dweet.io/dweet/for/" + thingName
	speak = wincl.Dispatch("SAPI.SpVoice") # invoking the builtin voice functionality in windows 10
	writePath = "D://LEO JOFEH/Documents/PACTICS/bc system demo/output/" # Path for writing local csv files


	def __init__(self):

		self.BCC = None
		self.opNum = None
		self.empNum = None
		self.eventType = None
		self.committed = 0
		self.storedEvents = []

		self.mode = "AUTO"
		self.lang = "KH"

		self.uniqueString = self.createRandomString()
		self.outputFilename = ''.join([_state.writePath, dt.datetime.now().strftime("%Y-%m-%d_"), self.uniqueString, ".csv"])

		print("Output will be written to", self.outputFilename)
		print("Realtime data will be streamed to https://www.dweet.io/follow/" + _state.thingName)

		# TODO - Allow for collecting config info from a specific file location, read it in line by line as now using the parse function. 
		# Might consider making a special code to allow to change the name of the device and it will update its own config file to match when changed that way.
		# Once implemented we should also send our name to dweet so we can see what data is from where, and check on downtime etc.

		# I think the first version of a dashboard would probably use this and trigger if a station is silent for too long etc. 

		self.prepLocalFile()

	def createRandomString(self,length=6):

		random.seed()
		lettersAndDigits = string.ascii_letters + string.digits
		return ''.join(random.choice(lettersAndDigits) for i in range(length))

	def parse(self, textInput):

		textInput = textInput.lower()

		# Checks for valid data entry and actions in auto mode

		if (self.mode=="AUTO"):

			# Checks for valid data in AUTO mode

			if(textInput.startswith('bc') and len(textInput)>2 and len(textInput)<12): # Then we have a bc number we should enter
				self.BCC = textInput
				return 1

			if(textInput.startswith('op') and len(textInput)>2 and len(textInput)<5): # Then we have a op number we should enter
				self.opNum = textInput
				return 1

			if(textInput.startswith('20') and len(textInput)>8 and len(textInput)<11): # Then we have a employee number we should enter
				self.empNum = textInput
				return 1

			# Checks for valid actions in AUTO mode

			if(textInput.startswith('act-') and len(textInput)>4 and len(textInput)<10): # Then we have an action to consider

				if (textInput.find('bgn1')!=-1): # Then we record a start event
					self.eventType="start1"
					return 1

				if (textInput.find('fin1')!=-1): # Then we record a start event
					self.eventType="finish1"
					return 1

				if (textInput.find('bgn2')!=-1): # Then we record a start event
					self.eventType="start2"
					return 1

				if (textInput.find('fin2')!=-1): # Then we record a start event
					self.eventType="finish2"
					return 1

				if (textInput.find('ok')!=-1): # Then the user wants to commit data, we should check if it's ok
					self.committed=1
					if (not self.isComplete()):
						self.committed = 0 # Keep us uncommitted if there's not enough data yet
					self.showEvent()
					return 1

				if (textInput.find('clr')!=-1): # The user wants to clear everything
					self.clearCurrent()
					print("Cleared all at user request")
					# Maybe add voice feedback here
					return 1

			print("Unrecognised command in AUTO mode") # Default if we don't understand any command here
			return 0

		print("Unrecognised mode")
		return 0

	def showEvent(self):

		print(self.BCC, self.opNum, self.empNum, self.eventType, self.committed)

	def isComplete(self):

		if (self.BCC!=None and self.opNum!=None and self.empNum!=None and self.eventType!=None and self.committed!=0):
			print("This event is complete")
			return 1
		else:
			return 0

	def clearCurrent(self):

		self.BCC = None
		self.opNum = None
		self.empNum = None
		self.eventType = None
		self.committed = 0

		print("Last event has been cleared - ready for new event")

		return 1

	def playSound(self, soundFileName):

		sp.Soundplayer(soundFileName)

		return 1

	def playVoice(self, asText):

		_state.speak.Speak(asText)
		
		return 1

	def prepLocalFile(self):

		f = open(self.outputFilename, "w")
		f.write(', '.join(["BCC", "EMP", "OP", "EVENT", ("TIME" + '\n')])) # comma separated values and builtin newline
		f.close()

		return 1

	def writeEventToLocalFile(self, strTime):

		# To do - think about modifying the file layout to more closely mirror existing BCC reports, so the event type field now dictates position in the row rather than being an entry of itself.

		f = open(self.outputFilename, "a")
		f.write(', '.join([self.BCC, self.empNum, self.opNum, self.eventType, (strTime + '\n')])) # comma separated values and builtin newline
		f.close()

		return 1

	def uploadEvent(self, strTime):

		# Package all data as a POST form

		payload = {
		"BCC" : self.BCC,
		"opNum" : self.opNum,
		"empNum" : self.empNum,
		"action" : self.eventType,
		"time" : strTime
		}

		# Post it and check the response, return 0 if bad response or timeout
		print("Attempting to POST")
		try:
			response = r.post(_state.dataEndpoint,data=payload, timeout=5)
			response.raise_for_status()
		except requests.exceptions.HTTPError as errh:
			print ("Http Error:",errh)
			return 0
		except requests.exceptions.ConnectionError as errc:
			print ("Error Connecting:",errc)
			return 0
		except requests.exceptions.Timeout as errt:
			print ("Timeout Error:",errt)
			return 0
		except requests.exceptions.RequestException as err:
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

   	# End class