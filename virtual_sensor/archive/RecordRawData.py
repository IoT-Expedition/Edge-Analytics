import struct
import math
import sys,getopt
import pexpect
import time
import struct
import binascii
import numpy as np
#import MySQLdb as sqldb
from time import gmtime, strftime
import time

DEFAULT_MAC_ADDRESS = "B0:B4:48:B8:9C:80"

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
		time.sleep(2)

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

#Form the query and post the data to the SQL db
def postData(dataToPost,sensorID,connection,cursorData,macAddress):
	if sensorID == 5:
		for element in dataToPost:
			queryStr = "INSERT INTO SynergySensorTagData (macAddr,sensorID,agcReading,time"+\
				") values ("
			queryStr += "'"+macAddress+"',"+str(sensorID)+",'"+element+"','"+\
				strftime("%Y-%m-%d %H:%M:%S", gmtime())+"')";
			sensorID+=1
			cursorData.execute(queryStr)
	else:
		queryStr = "INSERT INTO SynergySensorTagData (macAddr,sensorID,thlpReading,time"+\
				") values ("
		queryStr += "'"+macAddress+"',"+str(sensorID)+",'"+str(dataToPost)+"','"+\
			strftime("%Y-%m-%d %H:%M:%S", gmtime())+"')";
		cursorData.execute(queryStr)


	connection.commit()
	return

#Get the data from the sensor corresponding to that specific handle
def getData(handle):
	gattInterface.sendline('char-read-hnd '+handle)
	gattInterface.expect('\r\nCharacteristic value/descriptor: .* \r\n')
	dataStr = gattInterface.after.split(": ")[1]
	return dataStr.split()


#Get MAC address from command line
try:
	values,options = getopt.getopt(sys.argv[1:],"mf:")
except getopt.GetoptError:
	print "Unrecognised parameters"
	sys.exit(2)

values = dict(values)
if "-m" not in values:
	print "MAC Address is not specified\nUse default " + DEFAULT_MAC_ADDRESS
	macAddress = DEFAULT_MAC_ADDRESS
else:
	macAddress = values['-m']

if "-f" not in values:
	filename = ""
else:
	filename = values['-f']

#Connecting to the tag and switching on all the sensors
gattInterface = connectToTag(macAddress)
switchOnSensors(gattInterface)
time.sleep(1)


#Connect to SQL db
#connection = sqldb.connect('localhost', 'datalogger', 'logger', 'synergydb');
#cursorData = connection.cursor()
dataLog = {}
sensorID = 0

print "Start data collection"
data = np.zeros((100,14))
for i in range(0,99):
	#Get data from each sensor in the list one after each other on a pull basis
	#in an infinite loop
	line = ""

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
	data[i,:] = val
	print val

	#Post the data to an SQL db
	#postData(dataToPost,sensorID,connection,cursorData,macAddress)

if filename != "":
	np.save(filename+'.npy',data)
print data
	
