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

# Used in number announcements

import math

class _state:

	pwd = os.path.dirname(__file__) # Gets absolute path to the directory that contains this file, not calling location.
	thingName = "PACTICS_demo" # reference for dweet
	dataEndpoint = "https://www.dweet.io/dweet/for/" + thingName # This will move to __init__() for multiple instances, with names from config barcode.
	writePath = os.path.join(pwd,'../output/')
	# TODO add config path and handle config file reading and writing, maybe implement using pickle for simplicity. or using scan codes - neater.


	def __init__(self):

		self.BCC = None
		self.opNum = None
		self.empNum = None
		self.eventType = None
		self.committed = 0
		self.storedEvents = []

		self.timer = self.interactionTimer()
		self.sfx = self.soundController()

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

	def postIntitialState(): # TODO implement logging to initial state service.

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

	def freshStart(self):

		self.timer.clear()

		self.sfx.announceFreshStart()


	class interactionTimer:

		def __init__(self):

			self.startTime=None
			self.stopTime=None
			self.lastInteractionTime=None

		def start(self):
			self.startTime=time.time()

		def isUnstarted(self):

			if self.startTime==None:
				return 1
			else:
				return 0

		def stop(self):
			self.stopTime=time.time()

		def getTiming(self):

			self.lastInteractionTime = self.stopTime-self.startTime

			return self.lastInteractionTime

		def clear(self):

			self.startTime=None
			self.stopTime=None
			self.lastInteractionTime=None

	class soundController:

		def __init__(self):

			self.lang = "KH"
			self.speak = wincl.Dispatch("SAPI.SpVoice")

			print("SFX initialised")

		def voiceFromText(self, asText):

			self.speak.Speak(asText)

			return 1

		def announceFreshStart(self):

			if(self.lang=="KH"):
				ps.playsound(os.path.join(_state.pwd,'../Voice',"nextpersoncanstart_KH.mp3"),block=False)
			else:
				self.voiceFromText("Ready for new operation")

			return 1

		def announceCompleteState(self):

			if(self.lang=="KH"):
				ps.playsound(os.path.join(_state.pwd,'../Voice',"finishedthankyou_KH.mp3"),block=False)
			else:
				self.voiceFromText("Finished, thank you")

		def announceClearedAll(self):

			if(self.lang=="KH"):
				ps.playsound(os.path.join(_state.pwd,'../Voice',"cancelledstartagain_KH.mp3"),block=False)
			else:
				self.voiceFromText("All cleared.")

		def announceMissingInfo(self, bccnumber, employeenumber, operationnumber, action):

			# Always called when there is something missing

			if(self.lang=="KH"):
				ps.playsound(os.path.join(_state.pwd,'../Voice',"pleasedontforgettoput_KH.mp3"),block=True)
			else:
				self.voiceFromText("Don't forget to put")

			if not bccnumber:
				
				if(self.lang=="KH"):
					time.sleep(0.2)
					ps.playsound(os.path.join(_state.pwd,'../Voice',"bcccode_KH.mp3"),block=True)
				else:
					self.voiceFromText("BCC number")

			if not employeenumber:
				
				if(self.lang=="KH"):
					time.sleep(0.2)
					ps.playsound(os.path.join(_state.pwd,'../Voice',"employeenumber_KH.mp3"),block=True)
				else:
					self.voiceFromText("Employee number")

			if not operationnumber:
				
				if(self.lang=="KH"):
					time.sleep(0.2)
					ps.playsound(os.path.join(_state.pwd,'../Voice',"operationnumber_KH.mp3"),block=True)
				else:
					self.voiceFromText("operation number")

			if not action:

				if(self.lang=="KH"):
					time.sleep(0.2)
					ps.playsound(os.path.join(_state.pwd,'../Voice',"startorfinish_KH.mp3"),block=True)
				else:
					self.voiceFromText("if you are starting or finishing.")

			return 1

		def announceOperationNumber(self, opNum):

			n = int(opNum.split("op")[1]) # get a sensible number out of a string that looks like "op<int>""

			if(self.lang=="KH"):
				ps.playsound(os.path.join(_state.pwd,'../Voice',"operation_KH.mp3"),block=True)
				self.announceNumber(n)
			else:
				self.voiceFromText("operation"+str(n))

			return 1

		def announceOK(self):

			ps.playsound(os.path.join(_state.pwd,'../Voice',"ok_KH.mp3"),block=False)

		def announceProblem(self):

			# not currently useful but may be in the future

			if(self.lang=="KH"):
				ps.playsound(os.path.join(_state.pwd,'../Voice',"systemproblem_KH.mp3"),block=True)
			else:
				self.voiceFromText("Sorry, the system has a problem. Please call a supervisor.")

			return 1

		def announceNumber(self, number):

			# Takes an integer and speaks it. Only works up to 999. Can easily modify to support more.

			# Use a dictionary to refer to the filenames for ease of access

			KH_numbers = {
			0 : "zero_KH.mp3",
			1 : "one_KH.mp3",
			2 : "two_KH.mp3",
			3 : "three_KH.mp3",
			4 : "four_KH.mp3",
			5 : "five_KH.mp3",
			6 : "six_KH.mp3",
			7 : "seven_KH.mp3",
			8 : "eight_KH.mp3",
			9 : "nine_KH.mp3",
			10 : "ten_KH.mp3",
			20 : "twenty_KH.mp3",
			30 : "thirty_KH.mp3",
			40 : "forty_KH.mp3",
			50 : "fifty_KH.mp3",
			60 : "sixty_KH.mp3",
			70 : "seventy_KH.mp3",
			80 : "eighty_KH.mp3",
			90 : "ninety_KH.mp3",
			100: "hundred_KH.mp3"
			}

			number = int(float(number)) # Just in case

			if (number > 999 or number < 0): # it's an unsupported number
				return 0

			leftovers = number

			# Find multiples of one hundred in the number

			hundreds = math.floor(leftovers/100)
			leftovers = leftovers%100

			# Find multiples of ten in the number

			tens = math.floor(leftovers/10)
			leftovers = leftovers%10

			# Find units in the number

			ones = leftovers

			# print("hundreds:",hundreds,"tens:",tens,"ones:",ones)

			if self.lang == "KH":

				if hundreds>0:

					# say hundreds then "hundred"

					ps.playsound(os.path.join(_state.pwd,'../Voice',KH_numbers[hundreds]),block=True)

					ps.playsound(os.path.join(_state.pwd,'../Voice',KH_numbers[100]),block=True)

				if tens>0:

					# say the relevant multiple of ten

					tens = tens*10 # because there are unique names for all multiples of 10 less than 100

					ps.playsound(os.path.join(_state.pwd,'../Voice',KH_numbers[tens]),block=True)

				if ( (ones>0) or (hundreds == 0 and tens == 0) ):

					ps.playsound(os.path.join(_state.pwd,'../Voice',KH_numbers[ones]),block=True)

			else:

				self.voiceFromText(str(number)) # in english it's simple lol


			return 1




			
		

	# TODO consider adding a file handling class and a realtime data handling class so these functions all look cleaner.

   	# End class