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


DEFAULT_MAC_ADDRESS = "B0:B4:48:B8:9C:80"

SAMPLE_NUM = 10

#Lists containing the handles of the sensors to switch them on and to
#read the response from them

sensorHandleList = [
					'0x24', # IR Temperature Sensor
					'0x2C', # Humidity Sensor
					'0x44', # Light Sensor
					'0x34', # Pressure Sensor
					'0x3C', # Accelerometer,Gyrometer and Compass
					]

sensorHandleRespList = [
						'0x21', # IR Temperature Sensor
						'0x29', # Humidity Sensor
						'0x41', # Light Sensor
						'0x31', # Pressure Sensor
						'0x39', # Accelerometer,Gyrometer and Compass'''
						]

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
			sendString = 'char-write-cmd '+handle+' 7f:7f'
		else:
			sendString = 'char-write-cmd '+handle+' 01'
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
	temp = calculateUnsignedIntValue(ambTemp,2)/128.0
	return temp

def convertHumidity(humidityLevel):
	humidity = calculateUnsignedIntValue(humidityLevel,2)
	humidity = humidity - (humidity%4)
	humidity = ((-6.0) + 125.0 * (humidity/ 65535.0))
	return humidity

def convertLightPressure(level,typeVal):
	if typeVal == 1:
		level = calculateUnsignedIntValue(level,0)
	elif typeVal == 2:
		level = calculateUnsignedIntValue(level,3)
	mantissa = level & 0x0FFF
	exponent = (level >> 12) & 0xFF
	magnitude = pow(2.0, exponent)
	output = (mantissa * magnitude)
	return output/100.

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
		if handle == '0x21': #IR Temperature Sensor
			val[1] = convertTemperature(getData(handle));
		elif handle == '0x29': #Humidity Sensor
			val[2] = convertHumidity(getData(handle));
		elif handle == '0x41': #Light Sensor
			val[3] = convertLightPressure(getData(handle),1)
		elif handle == '0x31': #Pressure Sensor
			val[4] = convertLightPressure(getData(handle),2)
		elif handle == '0x39': # Accelerometer,Gyrometer and Compass
			temp = convertAGC(getData(handle))
	
	val = np.hstack((val,temp))

	return val

def areSensorReadingsValid():
	result = 0
	val = getAllSensorData()
	for i in range(14):
		if val[i] == 0:
			print "Warning: Sensor " + str(i) + " is returning 0."
			result = i
			break

	return result


#Get MAC address from command line
try:
	values,options = getopt.getopt(sys.argv[1:],"m:")
except getopt.GetoptError:
	print "Unrecognised parameters"
	sys.exit(2)

values = dict(values)
if "-m" not in values:
	print "MAC Address is not specified\nUse default " + DEFAULT_MAC_ADDRESS
	macAddress = DEFAULT_MAC_ADDRESS
else:
	macAddress = values['-m']

#Connecting to the tag and switching on all the sensors
print "Connecting to the SensorTag"
gattInterface = connectToTag(macAddress)
print "Turning on sensors"
switchOnSensors(gattInterface)
time.sleep(1)

# make sure all sensors are working
while areSensorReadingsValid() != 0:
	print "Some sensors are not workig. Turn on sensors again."
	switchOnSensors(gattInterface)

# start data sampling
samplingCount = 0;

print "Starting data collection"
data = np.zeros((100,14))
while True:
	# Get sensor readings and timestamp
	val = getAllSensorData()

	data = data[1:100,:]
	data = np.vstack((data,val))

	if samplingCount > SAMPLE_NUM:
		print "Ready to sample data"
		samplingCount = -1
	elif samplingCount != -1:
		samplingCount = samplingCount + 1		

	for path in glob.glob('cmd/*'):
		# Read JSON command
		cmd = json.loads(open(path).read())

		# Check if sensor directry exists. If not create
		dataDir = 'sensors/'+cmd['sensor']+'/samples/'
		if not os.path.exists(dataDir):
			os.makedirs(dataDir)
			meta = json.dumps([])
			open(dataDir + 'meta.json', 'w').write(meta)


		# Save data points to a file
		files = glob.glob(dataDir + '*')
		length = len(data)
		sample = data[length-cmd['sampleNum']:length,:]
		filename = str(len(files)) + '.csv'
		np.savetxt(dataDir + filename, sample, delimiter=',')

		# Save meta information
		meta = json.loads(open(dataDir + 'meta.json','r').read())
		cmd['filename'] = filename
		meta.append(cmd)
		open(dataDir + 'meta.json','w').write(json.dumps(meta))


		# Clean up
		os.remove(path)
		print "Sampled " + str(cmd['sampleNum']) + " data points to " + filename


	
