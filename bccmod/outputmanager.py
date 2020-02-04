# outputmanager.py
# (c) Leo Jofeh @ Bespokh.com September 2019
# Handles output like terminal info, logging and https

# imports

import platform
import string
import time
import datetime as dt
import os
import random
import configparser
import requests as r
from ISStreamer import Streamer
from ftplib import FTP
import threading
import shutil

class _outputManager():

	def __init__(self, station):

		self.station = station

		self.status = "GREEN" # This will be used for stack lights.

		# Check ANSI availability for terminal

		self.ANSI = True if platform.system().find('Linux')!=-1 else False # Check whether we can ANSI color format terminal output

		# ANSI style codes to prepend messages 

		self.NORM = '\033[0;37;40m' # Regular white text on black background
		self.ALERT = '\033[1;31;40m' # Bold red text on black background
		self.INFO = '\033[1;34;40m' # Bold blue text on black background
		self.SUCCESS = '\033[1;32;40m' # Bold green text on black background

		# CSV header string format

		self.CSVHeader = ','.join(["stationName", "stationLocation", "version", "uploadTime", "eventTime", "eventType", "bcc", "empNum", "opNum", "scrap", ("interactionTime"+"\n")])
		self.logHeader = ','.join(["BCC", "EMP", "OP", "EVENT", "TIME", "PTIME", ("SCRAP" + '\n')])

		# Get paths to vital folders

		self.writePath = os.path.join(os.path.dirname(__file__),'../output/')
		self.configPath = os.path.join(os.path.dirname(__file__),'../secrets/')
		self.cachePath = os.path.join(os.path.dirname(__file__),'../eventCache/')
		self.remotePath = self.getConfig('networkStorage','mountPath')

		# Check whether or not we should be logging

		self.logging = float(self.getConfig('DEFAULT', 'logging'))

		# Set up for local file writing

		self.outputFilename = ''.join([self.writePath, dt.datetime.now().strftime("%Y-%m-%d_"), self.createRandomString(), ".csv"])
		self.prepLocalFile(self.outputFilename)

		# Setup uploads daemon

		self.uploadDaemon = threading.Thread(target=self.handleUploads,daemon=True,args=())
		self.uploadsDaemonCycleTime = 15 # It runs every 15 seconds.
		self.payloadListLock=threading.Lock() # Ensure safe access to the following payload list
		self.payloadList = []

		# Now invoke the payloads daemon (which runs handleUploads) forever

		self.invokeUploadsDaemon()

		# Set up for dweet.io broadcasting

		self.setDweetThingName(self.getConfig('dweet','thingname')) # This may be changed later
		self.terminalOutput("Realtime data will be streamed to https://www.dweet.io/follow/{}".format(self.dweetThingName))

		# Set up InitialState broadcasting

		ISSconf = self.configPath+'stationConfig.ini'
		self.InitialStateStream = Streamer.Streamer(bucket_key="M5LW9T38AJ4T", bucket_name="pacticstester", debug_level=1, ini_file_location=ISSconf)

		# Set up for ftp uploads to local/remote folder (will become bc system endpoint in the future)

		self.ftpserver=self.getConfig('ftp','ftpserver')
		self.terminalOutput("BC system integration endpoint: {}".format(self.ftpserver))

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

	def getConfig(self,section,parameter):

		config=configparser.ConfigParser()
		config.read(self.configPath+'stationConfig.ini')
		try:
			return config[section][parameter]
		except:
			return None

	def setConfig(self,section,parameter,field):

		config=configparser.ConfigParser()
		config.read(self.configPath+'stationConfig.ini')
		config[section][parameter]=field

		with open(self.configPath+'stationConfig.ini','w') as configfile:
			config.write(configfile)

		return 1

	# Functions to do with local file handling

	def createRandomString(self,length=6):

		random.seed()
		lettersAndDigits = string.ascii_letters + string.digits
		return ''.join(random.choice(lettersAndDigits) for i in range(length))

	def prepLocalFile(self, filename):

		with open(filename, "w") as f:
			f.write(self.logHeader)

		return 1

	def pushEvent(self, payload):

		# TODO - think about modifying the file layout to more closely mirror existing BCC reports, so the event type field now dictates position in the row rather than being an entry of itself.

		# Write the event to the local log file in /output/ if logging is enabled from the config file

		if self.logging:
			try:			
				with open(self.outputFilename, "a") as f:
					f.write(', '.join([payload['BCC'], payload['empNum'], payload['opNum'], payload['eventType'], payload['time'].strftime("%d/%m/%Y_%H:%M:%S"), payload['interactionTime'], (payload['scrap'] + '\n')])) # comma separated values and builtin newline
			except:
				self.terminalOutput("LOGGING FAILURE - possible filesize issue", style='ALERT')
		# Now append the payload to the payload list using a lock, where the upload daemon will find it later.

		with self.payloadListLock:
			self.payloadList.append(payload)

		# With this done, the data is safely on the payload list, and the upload daemon will handle everything else from here.

		return 1
	
	# Dweet config

	def setDweetThingName(self,newname):

		self.setConfig('dweet','thingname',newname) # Set the new name in the config file, so it is permanent

		self.dweetThingName = self.getConfig('dweet','thingname') # Read it back to ensure that internal and external records are consistent
		self.dweetEndpoint = "https://www.dweet.io/dweet/for/" + self.dweetThingName # Set up the endpoint based on the new thingname.

	# Functions to do with InitialState

	def uploadEventToInitialState(self, payload):

		# Need to modify the time to the correct format before posting.

		payload['time']=payload['time'].strftime("%d/%m/%Y-%H:%M:%S")

		try:
			self.InitialStateStream.log_object(payload, key_prefix="")
			self.InitialStateStream.flush()
		except:
			return 0 # TODO Do something slightly more intelligent here
			
		return 1

	def writeToBCC(self, filename):

		try:
			ftp=FTP(self.ftpserver)
			ftp.login(user=self.getConfig('ftp','ftpuser'),passwd=self.getConfig('ftp','ftppswd'))
			ftp.cwd('./WindowsService/Inbound')
			ftp.storbinary('STOR '+filename, open(self.cachePath+filename,'rb'))
			# TODO - check what is the response here?
			ftp.quit()
			self.terminalOutput('FTP success',style='SUCCESS')
			return 1
		except:
			self.terminalOutput('FTP failure of some kind',style='ALERT')
			return 0

	def writeToBCCviaShareFolder(self, filename):

		# Copies a real results file to the remote directory specified in remotePath

		# Test whether the mount point is a real one here

		if not os.path.isdir(self.remotePath+'/uploads/'): # TODO modify this to be included in configuration
			self.terminalOutput('Remote folder not mounted, aborting upload attempt')

			# TODO In the future we can attempt to dynamically mount it here.
			return 0

		try:
			shutil.copyfile(self.cachePath+filename, self.remotePath+'/uploads/'+filename)
			self.terminalOutput('Remote to BCC - success',style='SUCCESS')
			return 1
		except:
			self.terminalOutput('Remote to BCC - failure, possibly mounting issue',style='ALERT')
			return 0

	# Upload daemon stuff

	def invokeUploadsDaemon(self):

		if (not self.uploadDaemon.isAlive()):
			self.uploadDaemon.start()

	def getTempFileNameByPayload(self, payload):

		# Creates a filename in the appropriate format for BC server ingestion given the contents of the payload

		uploadTime=dt.datetime.now()
		return payload['BCC'].upper()+'_'+uploadTime.strftime("%Y%m%d")+'_'+uploadTime.strftime("%H%M%S%f")[:-3]+'.csv'

	def writeEventFileToCache(self, payload):

		# Create the tempFilename, and get the path to the eventCache folder
		tempfilename = self.cachePath + self.getTempFileNameByPayload(payload)

		fileWriteOK=0
		tries=3
		while not fileWriteOK and tries:
			try:
				with open(tempfilename, "w") as f:

					f.write(self.CSVHeader)
					f.write(', '.join([self.station.name, self.station.location, self.station.version, payload['time'].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], payload['time'].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], payload['eventType'], payload['BCC'].upper(), payload['empNum'], payload['opNum'], payload['scrap'], (payload['interactionTime'] + '\n')]))
					# f.write(', '.join([payload['BCC'].upper(), payload['empNum'], payload['opNum'], payload['eventType'], payload['time'].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], payload['interactionTime'], (payload['scrap'] + '\n')]))
				fileWriteOK=1
			except:
				self.terminalOutput("File write failed once", style='ALERT')
				tries -=1

		return 1

	def handleUploads(self):

		self.terminalOutput("Uploads Daemon is alive",style='INFO')

		while True:
			time.sleep(self.uploadsDaemonCycleTime)

			# We just try to handle a single event per cycle.
			# Using the lock, try to pop an event off the payloadList (if there's anything on it). Release the lock

			thisPayload={}
			thisPayloadListLength=0

			with self.payloadListLock:

				thisPayloadListLength = len(self.payloadList)
				if thisPayloadListLength:

					thisPayload=self.payloadList.pop(0)

			if thisPayloadListLength:
				# Use the payload that we popped and write its info to a csv file in the eventCache

				self.writeEventFileToCache(thisPayload)

				# Use the payload object to attempt an upload to InitialState (forget dweet now) (it doesn't matter if it fails)

				self.uploadEventToInitialState(thisPayload) # Don't do it quietly because it eats stdout which affects input in the main loop.

			# Examine the eventCache folder and locate all files. Choose the first csv file in alphabetic order.

			cachedEvents = list(filter(lambda x: x.endswith('.csv'), os.listdir(self.cachePath))) # (don't .sort() on this because it retruns none for an empty list)

			if len(cachedEvents):

				self.terminalOutput('Attempting write an event file to remote folder, cache contains {} .csv files'.format(len(cachedEvents)),style='INFO')

				uploadTargetFilename = cachedEvents[0]

				# Attempt to ftp put this file in the remote directory. If it works, then delete it from the event cache.

				if self.writeToBCC(uploadTargetFilename):
					try:
						os.remove(os.path.join(self.cachePath,uploadTargetFilename))
					except OSError:
						self.terminalOutput("Temp file could not be deleted, moving on", style='ALERT')

				# If it doesn't work, then leave it there and we'll try again later (probably a network issue), but give me an error message
			else:
				self.terminalOutput('No files found to upload from event cache',style='INFO')

			# At this stage we have popped an event, written it to cache, and tried to upload 

			continue

		return 1 # It is unlikely that this will be killed while it is doing something but losing data very occasionally is ok.
