# outputmanager.py
# (c) Leo Jofeh @ Bespokh.com September 2019
# Handles output like terminal info, logging and https

# imports

import platform
import string
import datetime as dt
import os
import random
import requests as r
from ISStreamer import Streamer

class _outputManager():

	def __init__(self):

		# Check ANSI availability for terminal

		self.ANSI = True if platform.system().find('Linux')!=-1 else False # Check whether we can ANSI color format terminal output

		# ANSI style codes to prepend messages 

		self.NORM = '\033[0;37;40m' # Regular white text on black background
		self.ALERT = '\033[1;31;40m' # Bold red text on black background
		self.INFO = '\033[1;34;40m' # Bold blue text on black background
		self.SUCCESS = '\033[1;32;40m' # Bold green text on black background

		# Get paths to vital folders

		self.writePath = os.path.join(os.path.dirname(__file__),'../output/')
		self.configPath = os.path.join(os.path.dirname(__file__),'../secrets/')

		# Set up for local file writing

		self.outputFilename = ''.join([self.writePath, dt.datetime.now().strftime("%Y-%m-%d_"), self.createRandomString(), ".csv"])
		self.prepLocalFile()

		# Set up for dweet.io broadcasting

		self.setDweetThingName('PACTICS_demo') # This may be changed later
		self.terminalOutput("Realtime data will be streamed to https://www.dweet.io/follow/{}".format(self.dweetThingName))

		# Set up InitialState broadcasting

		conf = ''.join([self.configPath,"InitialStateConfig.ini"])
		self.InitialStateStream = Streamer.Streamer(bucket_key="M5LW9T38AJ4T", bucket_name="pacticstester", debug_level=1, ini_file_location=conf)

		self.terminalOutput("Output channels initialised")


	def terminalOutput(self, text, style='NORM'):

		# Supported styles

		if style=='NORM' or not self.ANSI:
			print(str(text))
			return
		if style=='ALERT' and self.ANSI:
			message = self.ALERT + text + self.NORM # Immediately default back to normal text
			print(message)
			return
		if style=='INFO' and self.ANSI:
			message = self.INFO + text + self.NORM
			print(message)
			return
		if style=='SUCCESS' and self.ANSI:
			message = self.SUCCESS + text + self.NORM
			print(message)
			return

	def loggingOutput(self, text):

		return

	def postingOutput(self, otherfields):

		return

	# Functions to do with local file handling

	def createRandomString(self,length=6):

		random.seed()
		lettersAndDigits = string.ascii_letters + string.digits
		return ''.join(random.choice(lettersAndDigits) for i in range(length))

	def prepLocalFile(self):

		with open(self.outputFilename, "w") as f:
			f.write(', '.join(["BCC", "EMP", "OP", "EVENT", "TIME", ("PTIME" + '\n')])) # comma separated values and builtin newline

		return 1

	def writeEventToLocalFile(self, BCC, empNum, opNum, eventType, now, interactionTime):

		# To do - think about modifying the file layout to more closely mirror existing BCC reports, so the event type field now dictates position in the row rather than being an entry of itself.

		#TODO - try this and report an error if it doesn't work.

		with open(self.outputFilename, "a") as f:
			f.write(', '.join([BCC, empNum, opNum, eventType, now, (str(interactionTime) + '\n')])) # comma separated values and builtin newline

		return 1

	# Functions to do with Dweet.io - NB this is a temporary service for debugging

	def setDweetThingName(self,newname):

		self.dweetThingName = newname
		self.dweetEndpoint = "https://www.dweet.io/dweet/for/" + newname 

	def uploadEventToDweet(self, BCC, empNum, opNum, eventType, now, interactionTime):

		# Package all data as a POST form

		payload = {
		"BCC" : BCC,
		"opNum" : opNum,
		"empNum" : empNum,
		"action" : eventType,
		"time" : now,
		"interactionTime" : interactionTime
		}

		# Post it and check the response, return 0 if bad response or timeout
		self.terminalOutput("Attempting to POST to Dweet.io")
		try:
			response = r.post(self.dweetEndpoint,data=payload, timeout=5)
			response.raise_for_status()
		except r.exceptions.HTTPError as errh:
			self.terminalOutput("Http Error: {}".format(errh),style='ALERT')
			return 0
		except r.exceptions.ConnectionError as errc:
			self.terminalOutput("Error Connecting: {}".format(errc),style='ALERT')
			return 0
		except r.exceptions.Timeout as errt:
			self.terminalOutput("Timeout Error: {}".format(errt),style='ALERT')
			return 0
		except r.exceptions.RequestException as err:
			self.terminalOutput("Oops: Something Else {}".format(err),style='ALERT')
			return 0

		self.terminalOutput("Good POST to Dweet.io",style='SUCCESS')
		return 1 

		# TODO occasionally or if the last upload worked then retry anything in storedEvents

	# Functions to do with InitialState

	def uploadEventToInitialState(self, BCC, empNum, opNum, eventType, now, interactionTime):

		payload = {
		"BCC" : BCC,
		"opNum" : opNum,
		"empNum" : empNum,
		"action" : eventType,
		"time" : now,
		"interactionTime" : interactionTime
		}

		try:
			self.InitialStateStream.log_object(payload, key_prefix="")
			self.InitialStateStream.flush()
		except:
			return 0 # Do something slightly more intelligent here
			
		return 1


	# TODO some config parsing stuff, all the naming and file writing etc, and 
	# for when we are running multi-day it should handle keeping multiple output files organised by day etc. 
	# CONSIDER implementing an auto-FTP upload for log files or results files on a certain schedule.
	# Consider using threading to handle remote upload etc and keep track of what is going on, and retries if the upload didn't work.

