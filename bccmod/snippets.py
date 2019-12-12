# snippets.py 

# File containing otherwise unused but possibly informative or useful code snippets from this project

# Functions to do with Dweet.io - NB this is a temporary service for debugging

def setDweetThingName(self,newname):

	self.setConfig('dweet','thingname',newname) # Set the new name in the config file, so it is permanent

	self.dweetThingName = self.getConfig('dweet','thingname') # Read it back to ensure that internal and external records are consistent
	self.dweetEndpoint = "https://www.dweet.io/dweet/for/" + self.dweetThingName # Set up the endpoint based on the new thingname.

def uploadEventToDweet(self, payload):

	# Post it and check the response, return 0 if bad response or timeout

	# Need to modify the time to the correct format before posting.

	payload['time']=payload['time'].strftime("%d/%m/%Y-%H:%M:%S")

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











# Need to modify the time to the correct format before posting.

		predt, micro= payload['time'].strftime("%Y-%m-%d %H:%M:%S.%f").split('.') # Which we need to strip to milliseconds (because %f is microseconds)
		predt="%s.%03d" % (predt, int(micro) / 1000)

		payload['time']=predt








		

# Placeholder function for prototyping FTP functionality for later integration with BCC backend.

	def writeToBCC(self, payload):

		# Only uploads a fake file right now

		# Need to modify the time to the correct format before posting.

		predt, micro= payload['time'].strftime("%Y-%m-%d %H:%M:%S.%f").split('.') # Which we need to strip to milliseconds (because %f is microseconds)
		predt="%s.%03d" % (predt, int(micro) / 1000)

		payload['time']=predt

		try:
			ftp=FTP(self.ftpserver)
			ftp.login(user=self.getConfig('ftp','ftpuser'),passwd=self.getConfig('ftp','ftppswd'))
			ftp.cwd('./upload')
			ftp.storbinary('STOR sample.txt', open(self.cachePath+'sample_push_data.csv.txt','rb'))
			ftp.quit()
			self.terminalOutput('FTP success',style='SUCCESS')
			return 1
		except:
			self.terminalOutput('FTP failure of some kind',style='ALERT')
			return 0

	def writeXML(self,payload):

		# Set up the filename

		tempfilename = ''.join([self.cachePath, dt.datetime.now().strftime("%Y-%m-%d_"), self.createRandomString(12), ".xml"])

		# Create an xml document object for writing to a folder somewhere, bcc will pick it up.

		eventXML=ET.Element("event")
		metadata=ET.SubElement(eventXML,"metadata")
		data=ET.SubElement(eventXML,"data")

		# Populate the metadata

		ET.SubElement(metadata,"station").text=self.station.name
		ET.SubElement(metadata,"location").text=self.station.location
		ET.SubElement(metadata,"version").text=self.station.version
		ET.SubElement(metadata,"uploadTime").text=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		# Populate the data

		ET.SubElement(data,"BCC").text=payload['BCC'].upper() # Put it in uppercase as required
		ET.SubElement(data,"empNum").text=payload['empNum']
		ET.SubElement(data,"opNum").text=payload['opNum'][2:] # Just the number, this is hacky right now
		ET.SubElement(data,"eventType").text=payload['eventType']
		ET.SubElement(data,"scrap").text=payload['scrap']
		ET.SubElement(data,"interactionTime").text=payload['interactionTime']

		# Modify the time format
		predt, micro= payload['time'].strftime("%Y-%m-%d %H:%M:%S.%f").split('.') # Which we need to strip to milliseconds (because %f is microseconds)
		predt="%s.%03d" % (predt, int(micro) / 1000)
		ET.SubElement(data,"eventTime").text=predt

		tree=ET.ElementTree(eventXML)
		try:
			tree.write(tempfilename, xml_declaration=True, encoding='utf-8')
		except:
			# This essentially means that the data is lost.
			self.terminalOutput("XML write to local folder failed",style='ALERT')
			return 0
		return 1
