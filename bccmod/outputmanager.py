# outputmanager.py
# (c) Leo Jofeh @ Bespokh.com September 2019
# Handles output like terminal info, logging and https

# imports

import platform

class _outputManager():

	def __init__(self):

		self.ANSI = True if platform.system().find('Linux')!=-1 else False # Check whether we can ANSI color format terminal output

		# ANSI style codes to prepend messages 

		self.NORM = '\033[0;37;40m' # Regular white text on black background
		self.ALERT = '\033[1;31;40m' # Bold red text on black background
		self.INFO = '\033[1;34;40m' # Bold blue text on black background
		self.SUCCESS = '\033[1;32;40m' # Bold green text on black background


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

	# TODO this still needs to manage file preparation, some config parsing stuff, all the naming and file writing etc, and 
	# for when we are running multi-day it should handle keeping multiple output files organised by day etc. 
	# CONSIDER implementing an auto-FTP upload for log files or results files on a certain schedule.
	# Consider using threading to handle remote upload etc and keep track of what is going on, and retries if the upload didn't work.

