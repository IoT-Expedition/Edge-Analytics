import struct
import math
import sys,getopt
import pexpect
import time
import struct
import binascii
#import MySQLdb as sqldb
from time import gmtime, strftime

DEFAULT_MAC_ADDRESS = "C4:BE:84:70:BB:85"

#Lists containing the handles of the sensors to switch them on and to
#read the response from them

sensorHandleList = ['0x24', # IR Temperature Sensor
					'0x2C', # Humidity Sensor
					'0x44', # Light Sensor
					'0x34', # Pressure Sensor
					'0x3C', # Accelerometer,Gyrometer and Compass
					]

sensorHandleRespList = ['0x21', # IR Temperature Sensor
						'0x29', # Humidity Sensor
						'0x41', # Light Sensor
						'0x31', # Pressure Sensor
						'0x39', # Accelerometer,Gyrometer and Compass'''
						]

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
			sendString = 'char-write-cmd '+handle+' 3f:3f'
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
	return str(temp)

def convertHumidity(humidityLevel):
	humidity = calculateUnsignedIntValue(humidityLevel,2)
	humidity = humidity - (humidity%4)
	humidity = ((-6.0) + 125.0 * (humidity/ 65535.0))
	return str(humidity)

def convertLightPressure(level,typeVal):
	if typeVal == 1:
		level = calculateUnsignedIntValue(level,0)
	elif typeVal == 2:
		level = calculateUnsignedIntValue(level,3)
	mantissa = level & 0x0FFF
	exponent = (level >> 12) & 0xFF
	magnitude = pow(2.0, exponent)
	output = (mantissa * magnitude)
	return str(output/100)

def convertAGC(agcLevel):
	xyzVals = []
	xyzVals.append(str(calculateSignedIntValue(agcLevel,2)*(500.0 / 65536.0))+","
		+str(calculateSignedIntValue(agcLevel,0)*(500.0 / 65536.0) * -1)+","
		+str(calculateSignedIntValue(agcLevel,4)*(500.0 / 65536.0)))
	xyzVals.append(str((calculateSignedIntValue(agcLevel,6)/16384.0))+","
		+str((calculateSignedIntValue(agcLevel,8)/16384.0))+","
		+str((calculateSignedIntValue(agcLevel,10)/16384.0)))
	return xyzVals

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
gattInterface = connectToTag(macAddress)
switchOnSensors(gattInterface)
time.sleep(1)


#Connect to SQL db
#connection = sqldb.connect('localhost', 'datalogger', 'logger', 'synergydb');
#cursorData = connection.cursor()
dataLog = {}
sensorID = 0
while True:
	#Get data from each sensor in the list one after each other on a pull basis
	#in an infinite loop
	for handle in sensorHandleRespList:
		if handle == '0x21': #IR Temperature Sensor
			dataToPost = convertTemperature(getData(handle));
			sensorID = 1
		elif handle == '0x29': #Humidity Sensor
			dataToPost = convertHumidity(getData(handle));
			sensorID = 2
		elif handle == '0x41': #Light Sensor
			dataToPost = convertLightPressure(getData(handle),1)
			sensorID = 3
		elif handle == '0x31': #Pressure Sensor
			dataToPost = convertLightPressure(getData(handle),2)
			sensorID = 4
		elif handle == '0x39': # Accelerometer,Gyrometer and Compass
			dataToPost = convertAGC(getData(handle))
			sensorID = 5
		print dataToPost
	#Post the data to an SQL db
	#postData(dataToPost,sensorID,connection,cursorData,macAddress)
	
	
