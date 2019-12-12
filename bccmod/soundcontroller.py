# soundcontroller.py
# (c) Leo Jofeh @ bespokh.com September 2019

import time

import os

import math

import contextlib

try:
	import win32com.client as wincl # modify for other platforms
	print('text2voice using win32com SAPI native')
	t2v = True
except ImportError:
	print('No native text2voice system available. Skipping.')
	t2v = False

with contextlib.redirect_stdout(None):
	import pygame.mixer as mix # This will handle sound from now on (but we supress the stupid output message)

class _soundController:

	def __init__(self, station):

		self.station = station

		self.status = "GREEN" # This will be used for stack lights.

		self.lang = self.station.output.getConfig('DEFAULT','lang')
		self.speak = wincl.Dispatch("SAPI.SpVoice") if t2v else None # TODO adjust for different operating systems.

		self.voicePath = os.path.join(os.path.dirname(__file__),'../Voice/')
		
		mix.init() # Starts the pygame sound mixer

		self.lastcommands = None

		self.KH_samples = { # These files are available in ./Voices/
		"freshstart":"nextpersoncanstart_KH.mp3",
		"complete":"finishedthankyou_KH.mp3",
		"clearall":"cancelledstartagain_KH.mp3",
		"missing":"pleasedontforgettoput_KH.mp3",
		"bcc":"bcccode_KH.mp3",
		"employee":"employeenumber_KH.mp3",
		"operationnumber":"operationnumber_KH.mp3",
		"startorfinish":"startorfinish_KH.mp3",
		"operation":"operation_KH.mp3",
		"ok":"ok_KH.mp3",
		"problem":"systemproblem_KH.mp3",
		"start":"start_KH.mp3",
		"stop":"stop_KH.mp3",
		"firsttime":"firsttime_KH.mp3",
		"secondtime":"secondtime_KH.mp3",
		"easterBarang":"barangSpeakKhmer_KH.mp3",
		"easterDutch":"egg_NL.mp3",
		"easterKhmer":"thanksReaksmey_KH.mp3",
		"point":"point_KH.mp3",
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

		self.EN_t2v_samples = { # For use with the system builtin text2speech functionality
		"freshstart":"Ready for new operation.",
		"complete":"Finished, thank you.",
		"clearall":"All cleared.",
		"missing":"Don't forget to put",
		"bcc":"BCC number",
		"employee":"Employee number",
		"operationnumber":"Operation number",
		"startorfinish":"if you are starting or finishing.",
		"operation":"operation",
		"ok":"OK",
		"problem":"Sorry, the system has a problem. Please call a supervisor."
		}

		print("SFX initialised")

	def announce(self, commands, blockbydefault=False):

		# Take a list of commands and announce them in a row. Keep a record of the last command list in case we need to repeat.

		if(not isinstance(commands,list)): 
			commands = [commands] # ensure it's a list

		self.lastcommands = commands # record this command set as the last thing we did.

		for index, message in enumerate(commands):

			if(self.lang=="KH"):
				mix.music.load(os.path.join(self.voicePath,self.KH_samples[message]))
				mix.music.play()
				#TODO check if there's some way to preload a bunch of samples in a row?
				if (index+1)!=len(commands): # This command has one coming after it
					blocking=True # Make sure that commands don't pile up in a row.
				else:
					blocking=False
				if blocking or blockbydefault:
					while mix.music.get_busy() == True:
					    continue
			else: 

				if isinstance(message, int):
					self.voiceFromText(str(message)) # Handles numbers 
				else:
					self.voiceFromText(self.EN_t2v_samples[message])

	def repeatLast(self): 

		if (self.lastcommands != None): # There was a latest command

			self.announce(self.lastcommands)

	def voiceFromText(self, asText):

		if t2v:
			self.speak.Speak(asText)

		return 1

	def announceFreshStart(self):

		self.announce('freshstart')

	def announceCompleteState(self):

		self.announce('complete', blockbydefault=True)

	def announceClearedAll(self):

		self.announce('clearall')

	def announceMissingInfo(self, payload): # TODO modify to accept a payload instead of individual numbers

		# Always called when there is something missing

		cmd = ['missing']

		if not payload['BCC']:
			
			cmd.append('bcc')

		if not payload['empNum']:
			
			cmd.append('employee')

		if not payload['opNum']:
			
			cmd.append('operationnumber')

		if not payload['eventType']:

			cmd.append('startorfinish')

		self.announce(cmd)

	def announceOperationNumber(self, opNum):

		n = int(opNum.split("op")[1]) # get a sensible number out of a string that looks like "op<int>""

		cmd=['operation']

		for message in self.numberAsCommand(n):

			cmd.append(message)

		self.announce(cmd)

	def announceCombo(self, payload):

		cmd=['operation']
		n = int(payload['opNum'].split("op")[1])
		for number in self.numberAsCommand(n):
			cmd.append(number)
		if payload['eventType'][0:3]=='bgn': #TODO this is too hacky right now - sort it out nicely.
			cmd.append('start')
		elif payload['eventType'][0:3]=='fin':
			cmd.append('stop')
		if payload['eventType'][3]=='1':
			cmd.append('firsttime')
		elif payload['eventType'][3]=='2':
			cmd.append('secondtime')

		self.announce(cmd)

	def announceOK(self):

		self.announce('ok')

	def announceProblem(self):

		# not currently useful but may be in the future

		self.announce('problem')

	def announceEgg(self, easterString):

		# Three options currently supported: vrijmibo, somleng and songha. Put more here if you want.

		if easterString=='vrijmibo':
			self.announce('easterDutch')
		elif easterString=='somleng':
			self.announce('easterKhmer')
		elif easterString=='songha':
			self.announce('easterBarang')

	def numberAsCommand(self, number):

		# Takes an integer and oututs a list of commands to produce it in speech. Only works up to 999. Can easily modify to support more.

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

		cmd = []

		if self.lang == "KH":

			if hundreds>0:

				# say hundreds then "hundred"

				cmd.append(hundreds)
				cmd.append(100)

			if tens>0:

				# say the relevant multiple of ten

				tens = tens*10 # because there are unique names for all multiples of 10 less than 100

				cmd.append(tens)

			if ( (ones>0) or (hundreds == 0 and tens == 0) ):

				cmd.append(ones)

		else:

			cmd.append(number) # Return the number as is for EN speaking purposes

		return cmd
