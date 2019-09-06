# soundcontroller.py
# (c) Leo Jofeh @ bespokh.com September 2019

import time

import os

import math

import win32com.client as wincl # modify for other platforms

import playsound as ps # should be platform agnostic

class _soundController:

	def __init__(self, pwd): # Must include a pwd reference so we can access sound files etc.

		self.lang = "KH"
		self.speak = wincl.Dispatch("SAPI.SpVoice") # TODO adjust for different operating systems.
		self.pwd = pwd

		print("SFX initialised")

	def voiceFromText(self, asText):

		self.speak.Speak(asText)

		return 1

	def announceFreshStart(self):

		if(self.lang=="KH"):
			ps.playsound(os.path.join(self.pwd,'../Voice',"nextpersoncanstart_KH.mp3"),block=False)
		else:
			self.voiceFromText("Ready for new operation")

		return 1

	def announceCompleteState(self):

		if(self.lang=="KH"):
			ps.playsound(os.path.join(self.pwd,'../Voice',"finishedthankyou_KH.mp3"),block=False)
		else:
			self.voiceFromText("Finished, thank you")

	def announceClearedAll(self):

		if(self.lang=="KH"):
			ps.playsound(os.path.join(self.pwd,'../Voice',"cancelledstartagain_KH.mp3"),block=False)
		else:
			self.voiceFromText("All cleared.")

	def announceMissingInfo(self, bccnumber, employeenumber, operationnumber, action):

		# Always called when there is something missing

		if(self.lang=="KH"):
			ps.playsound(os.path.join(self.pwd,'../Voice',"pleasedontforgettoput_KH.mp3"),block=True)
		else:
			self.voiceFromText("Don't forget to put")

		if not bccnumber:
			
			if(self.lang=="KH"):
				time.sleep(0.2)
				ps.playsound(os.path.join(self.pwd,'../Voice',"bcccode_KH.mp3"),block=True)
			else:
				self.voiceFromText("BCC number")

		if not employeenumber:
			
			if(self.lang=="KH"):
				time.sleep(0.2)
				ps.playsound(os.path.join(self.pwd,'../Voice',"employeenumber_KH.mp3"),block=True)
			else:
				self.voiceFromText("Employee number")

		if not operationnumber:
			
			if(self.lang=="KH"):
				time.sleep(0.2)
				ps.playsound(os.path.join(self.pwd,'../Voice',"operationnumber_KH.mp3"),block=True)
			else:
				self.voiceFromText("operation number")

		if not action:

			if(self.lang=="KH"):
				time.sleep(0.2)
				ps.playsound(os.path.join(self.pwd,'../Voice',"startorfinish_KH.mp3"),block=True)
			else:
				self.voiceFromText("if you are starting or finishing.")

		return 1

	def announceOperationNumber(self, opNum):

		n = int(opNum.split("op")[1]) # get a sensible number out of a string that looks like "op<int>""

		if(self.lang=="KH"):
			ps.playsound(os.path.join(self.pwd,'../Voice',"operation_KH.mp3"),block=True)
			self.announceNumber(n)
		else:
			self.voiceFromText("operation"+str(n))

		return 1

	def announceOK(self):

		ps.playsound(os.path.join(self.pwd,'../Voice',"ok_KH.mp3"),block=False)

	def announceProblem(self):

		# not currently useful but may be in the future

		if(self.lang=="KH"):
			ps.playsound(os.path.join(self.pwd,'../Voice',"systemproblem_KH.mp3"),block=True)
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

				ps.playsound(os.path.join(self.pwd,'../Voice',KH_numbers[hundreds]),block=True)

				ps.playsound(os.path.join(self.pwd,'../Voice',KH_numbers[100]),block=True)

			if tens>0:

				# say the relevant multiple of ten

				tens = tens*10 # because there are unique names for all multiples of 10 less than 100

				ps.playsound(os.path.join(self.pwd,'../Voice',KH_numbers[tens]),block=True)

			if ( (ones>0) or (hundreds == 0 and tens == 0) ):

				ps.playsound(os.path.join(self.pwd,'../Voice',KH_numbers[ones]),block=True)

		else:

			self.voiceFromText(str(number)) # in english it's simple lol


		return 1

	def repeatLast(self): # TODO make this work to repeat the last thing we said, and do nothing if there was no last announcement
		return 0


# import pygame    since playsound doesn't work nicely on linux because of gstreamer apparently.
# pygame.mixer.init()
# pygame.mixer.music.load("myFile.wav")
# pygame.mixer.music.play()
# while pygame.mixer.music.get_busy() == True:
#     continue