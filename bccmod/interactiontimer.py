# interactiontimer.py
# (c) Leo Jofeh @ bespokh.com September 2019

import time

class _interactionTimer:

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
