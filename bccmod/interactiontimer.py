# interactiontimer.py
# (c) Leo Jofeh @ bespokh.com September 2019

import time
import threading # Used for stayalive daemon

class _interactionTimer:

	def __init__(self, station):

		self.station = station

		self.status = "GREEN" # This will be used for stack lights.

		self.startTime=None
		self.stopTime=None
		self.lastInteractionTime=None

		self.lastInputTime=time.time()
		self.stayAliveCycleTime = 60 # [seconds]

		self.stayAliveDaemon = threading.Thread(target=self.stayAlive,daemon=True,args=())

	def startKeepAlive(self):

		if (not self.stayAliveDaemon.isAlive()):
			self.stayAliveDaemon.start()

	def start(self):
		self.startTime=time.time()

	def isUnstarted(self):

		return 1 if self.startTime==None else 0

	def stop(self):
		self.stopTime=time.time()

	def getTiming(self):

		self.lastInteractionTime = self.stopTime-self.startTime

		return self.lastInteractionTime

	def clear(self):

		self.startTime=None
		self.stopTime=None
		self.lastInteractionTime=None

	def registerActiveInput(self):

		self.lastInputTime=time.time()

	def stayAlive(self):

		while True:
			time.sleep(5)
			if (time.time() - self.lastInputTime > self.stayAliveCycleTime):
				print("\n~StayAlive~\nScan something: ",end='')
				self.registerActiveInput()
			continue
