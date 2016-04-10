import struct
import math
import sys,getopt
import pexpect
import time
import struct
import binascii
import numpy as np
import time
import glob
import os
import json
import threading
from predict import predictWithData
import warnings
from BuildingDepotHelper import BuildingDepotHelper
from giottoSetting import giottoSetting 

SAMPLING_FLAG_PATH = "state/sampling"
DEFAULT_MAC_ADDRESS = "B0:B4:48:B8:9C:80"
#DEFAULT_MAC_ADDRESS = "B0:B4:48:B9:9D:87"
latestReadings = np.zeros((1,13))
samplingRates = {}

#Lists containing the handles of the sensors to switch them on and to
#read the response from them

sensorTypeList = ['Temperature',
				 'Humidity',
				 'Lux',
				 'Pressure',
				 'Accelerometer X',
				 'Accelerometer Y',
				 'Accelerometer Z',
				 'Gyrometer X',
				 'Gyrometer Y',
				 'Gyrometer Z',
				 'Magnetomitor X',
				 'Magnetomitor Y',
				 'Magnetomitor Z',
				 ]

sensorHandleList = ['0x24', # IR Temperature Sensor
					'0x2C', # Humidity Sensor
					'0x44', # Light Sensor
					'0x34', # Pressure Sensor
					'0x3C', # Accelerometer,Gyrometer and Compass
					]

sensorHandleRespList = ['0x0021', # IR Temperature Sensor
						'0x0029', # Humidity Sensor
						'0x0041', # Light Sensor
						'0x0031', # Pressure Sensor
						'0x0039', # Accelerometer,Gyrometer and Compass'''
						]

sensorHandleNotifList = ['0x22', # IR Temperature Sensor
						'0x2A', # Humidity Sensor
						'0x42', # Light Sensor
						'0x32', # Pressure Sensor
						'0x3A', # Accelerometer,Gyrometer and Compass'''
						]
sensorHandlePeriodList = ['0x0026', #IR Temperature Sensor
						'0x002E', # Humidity Sensor
						'0x0026', # Light Sensor
						'0x0036', # Pressure Sensor
						'0x003E', # Motion Sensor
						]

class DataStoreThread(threading.Thread):
    def __init__(self, n, t):
        super(DataStoreThread, self).__init__()
        self.n = n
        self.t = t
        self.data = np.zeros((30,14))
        self.latestReadings = np.zeros((1,13))
        self.count = 0
        self.command = ''
        self.flag = 1;
        self.bdHelper = BuildingDepotHelper()

    def run(self):
    	print "Sampling started"
    	while self.flag == 1:
        	for i in range(30):
        		time.sleep(self.t)
        		self.data[i,0] = current_milli_time()
        		self.data[i,1:14] = latestReadings[0,0:13]
        		#print self.data[i,1:14]
           
        	prediction = predictWithData('knocking', self.data)
        	print str(time.time()) + ' : ' + prediction
        	
        	self.bdHelper.postData('b90cac66-ae49-4e6d-9de5-12aed18e6a64',prediction)
        	#self.bdHelper.postData('7858c6ef-efa8-4f38-8dca-43c7463b7fb8',prediction)
        	if prediction == 'knocking':
        		value = 1
        	else:
        		value = 0

        	self.bdHelper.postData('725ac9c0-b786-4bfe-8830-3fe97e1fd45d',value)
        	#self.bdHelper.postData('92890ce2-2bf6-409b-9ed0-c820bc0431de',value)
        		



    def setData(self, index, val):
        self.latestReadings[0,index:index+val.size] = val

    def setFlag(self, flag):
    	self.flag = flag


def current_milli_time():
	return int(round(time.time() * 1000))

#Driving the gatttool via pexpect to connect to the SensorTag
def connectToTag(macAddress):
	gattInterface = pexpect.spawn('gatttool -b '+macAddress+' --interactive')
	gattInterface.expect('\[LE\]')
	gattInterface.sendline('connect')
	return gattInterface

#Commands sent to the SensorTag to switch on the sensors
def switchOnSensors(gattInterface):
	for handle in sensorHandleList:
		if handle == '0x3C':
			sendString = 'char-write-cmd '+handle+' 7f:00'
		else:
			sendString = 'char-write-cmd '+handle+' 01'
		gattInterface.sendline(sendString)
		gattInterface.expect('\[CON\]')

#Commands sent to the SensorTag to switch on notifications for each
#individual sensor
def setNotifications(gattInterface, isEnabled):
	for handle in sensorHandleNotifList:
		if isEnabled == 1:
			sendString = 'char-write-cmd '+handle+' 01:00'
		else:
			sendString = 'char-write-cmd '+handle+' 00:00'
		gattInterface.sendline(sendString)
		gattInterface.expect('\[CON\]')

#Get the integer value from the hex bytes we have 
def calculateIntValue(valueList,offset):
	hexStr = binascii.unhexlify(valueList[offset]+valueList[offset+1])
	intValue = struct.unpack('>h',hexStr)
	return int(intValue[0])

#Get the unsigned integer value from the hex bytes we have
def calculateUnsignedIntValue(valueList,offset):
	intValue = (int(valueList[offset+1],16)<<(8))+(int(valueList[offset],16))
	return intValue

#Get the signed integer value from the hex bytes we have
def calculateSignedIntValue(valueList,offset):
	hexStr = binascii.unhexlify(valueList[offset]+valueList[offset+1])
	intValue = struct.unpack('<h',hexStr)
	return int(intValue[0])

#The below four functions are for getting the numerical value of the
#sensor's output from the hex data we have

def convertTemperature(ambTemp):
	val = np.zeros((1))
	val[0] = calculateUnsignedIntValue(ambTemp,2)/128.0
	return val

def convertHumidity(humidityLevel):
	val = np.zeros((1))
	humidity = calculateUnsignedIntValue(humidityLevel,2)
	humidity = humidity - (humidity%4)
	humidity = ((-6.0) + 125.0 * (humidity/ 65535.0))
	val[0] = humidity
	return val

def convertLightPressure(level,typeVal):
	val = np.zeros((1))
	if typeVal == 1:
		level = calculateUnsignedIntValue(level,0)
	elif typeVal == 2:
		level = calculateUnsignedIntValue(level,3)
	mantissa = level & 0x0FFF
	exponent = (level >> 12) & 0xFF
	magnitude = pow(2.0, exponent)
	output = (mantissa * magnitude)
	val[0] = output / 100
	return val

def convertAGC(agcLevel):
	values = np.zeros((9))
	values[0] = calculateSignedIntValue(agcLevel,0) / 128.
	values[1] = calculateSignedIntValue(agcLevel,2) / 128.
	values[2] = calculateSignedIntValue(agcLevel,4) / 128.
	values[3] = calculateSignedIntValue(agcLevel,6) / 4096.
	values[4] = calculateSignedIntValue(agcLevel,8) / 4096.
	values[5] = calculateSignedIntValue(agcLevel,10)/ 4096.
	values[6] = calculateSignedIntValue(agcLevel,12)/ (32768. / 4912.)
	values[7] = calculateSignedIntValue(agcLevel,14)/ (32768. / 4912.)
	values[8] = calculateSignedIntValue(agcLevel,16)/ (32768. / 4912.)

	return values

def saveSample(samples):
	# Save data points to a file
	filename = 'test.csv'
	np.savetxt(filename, samples, delimiter=',')

	print "Sampled " + str(samples.size) + " data points to " + filename

#Get sampling rate
def getSamplingRates():
	rates = {}
	for handle in sensorHandlePeriodList:
		sendString = 'char-read-hnd ' + handle
		gattInterface.sendline(sendString)
		gattInterface.expect('\r\nCharacteristic value/descriptor: .* \r\n')
		dataStr = gattInterface.after.split(": ")[1]
		time.sleep(0.5)
		rates[handle] = dataStr

	return rates

# Set sampling rates with map
def setSamplingRates(valueStrings):
	for handle in sensorHandlePeriodList:
		sendString = 'char-write-cmd ' + handle + " " + valueStrings[handle]
		gattInterface.sendline(sendString)

# Set a sampling rate to all sensors
def setSamplingRate(samplingRate):
	val = samplingRate * 100

	for handle in sensorHandlePeriodList:
		# check minimal sampling
		if handle == '0x0026' or handle == '0x0026':
			val = 100 * max(0.3, samplingRate)
		else:
			val = 100 * max(0.1, samplingRate)

		valString = hex(int(val))[2:]
		if len(valString) == 1:
			valString = '0' + valString

		sendString = 'char-write-cmd ' + handle + " " + valString
		gattInterface.sendline(sendString)
		gattInterface.expect('\[CON\]')


#Get the data from the sensor corresponding to that specific handle
def getData(handle):
	gattInterface.sendline('char-read-hnd '+handle)
	gattInterface.expect('\r\nCharacteristic value/descriptor: .* \r\n')
	dataStr = gattInterface.after.split(": ")[1]
	return dataStr.split()

def getAllSensorData():
	val = np.zeros((5))
	val[0] = current_milli_time()

	for handle in sensorHandleRespList:
		if handle == '0x0021': #IR Temperature Sensor
			val[1] = convertTemperature(getData(handle));
		elif handle == '0x0029': #Humidity Sensor
			val[2] = convertHumidity(getData(handle));
		elif handle == '0x0041': #Light Sensor
			val[3] = convertLightPressure(getData(handle),1)
		elif handle == '0x0031': #Pressure Sensor
			val[4] = convertLightPressure(getData(handle),2)
		elif handle == '0x0039': # Accelerometer,Gyrometer and Compass
			temp = convertAGC(getData(handle))
	
	val = np.hstack((val,temp))

	return val

def areSensorReadingsValid():
	result = 0
	val = getAllSensorData()
	for i in range(14):
		if val[i] == 0:
			print "Warning: " + sensorTypeList[i] + " sensor is returning 0."
			result = i
			break

	return result

def extractValuesFromDataString(dataString):
	# extract a handle
	dataString = dataString.strip().split(" value: ")
	handle = dataString[0].split(' = ')[1]

	# extract a data part
	index = sensorHandleRespList.index(handle)
	data = dataString[1].split();

	if handle == '0x0021': #IR Temperature Sensor
		val = convertTemperature(data);
	elif handle == '0x0029': #Humidity Sensor
		val = convertHumidity(data);
	elif handle == '0x0041': #Light Sensor
		val = convertLightPressure(data,1)
	elif handle == '0x0031': #Pressure Sensor
		val = convertLightPressure(data,2)
	elif handle == '0x0039': # Accelerometer,Gyrometer and Compass
		val = convertAGC(data)


	index = sensorHandleRespList.index(handle)
	latestReadings[0,index:index+val.size] = val	

	return val

# Main function
if __name__ == "__main__":
	warnings.filterwarnings('ignore')

	SAMPLING_RATE = 0.1
	MAX_SAMPLING_NUMBER = 30


	#Get MAC address from command line
	try:
		values,options = getopt.getopt(sys.argv[1:],"m:")
	except getopt.GetoptError:
		print "Unrecognised parameters"
		sys.exit(2)

	values = dict(values)
	if "-m" not in values:
		setting = giottoSetting()
		macAddress = setting.get('default_sensor_tag')
		print "MAC Address is not specified\nUse default " + macAddress
	else:
		macAddress = values['-m']
		print "MAC Address is specified: " + macAddress


	#Connecting to the tag and switching on all the sensors
	print "Connecting to the SensorTag"
	gattInterface = connectToTag(macAddress)
	print "Turning on sensors"
	switchOnSensors(gattInterface)
	time.sleep(1)

	# make sure all sensors are working
	while areSensorReadingsValid() != 0:
		print "Some sensors are not initialized. Turning on sensors again."
		switchOnSensors(gattInterface)
		time.sleep(1)

	# configure sampling rates
	setNotifications(gattInterface,0)
	setSamplingRate(0.1)

	# turn on notificaitons
	setNotifications(gattInterface, 1)

	# start data sampling
	samplingCount = 0;

	print "Starting data collection"

	dataStoreThread = DataStoreThread(MAX_SAMPLING_NUMBER, SAMPLING_RATE)
	dataStoreThread.start()

	try:
		while True:
			#Process each notification as it is received and convert the sensor value
			#according to the handle
			gattInterface.expect('\r\nNotification handle = .* \r\n')
			receivedString = gattInterface.after

			# split lines because multiple data can be notified at the same time
			dataStrings = receivedString.strip().split("\r\n")
			for dataString in dataStrings:
				if dataString[0:5] != "[CON]":	# neglect commnad lines
					val = extractValuesFromDataString(dataString)

	except (KeyboardInterrupt, SystemExit):
		dataStoreThread.setFlag(0)
		sys.exit()


		
