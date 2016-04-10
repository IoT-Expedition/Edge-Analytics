import struct
import math
import sys,getopt
import pexpect
import time
import struct
import random
import binascii
import json
import requests
from calendar import timegm
from time import gmtime, strftime

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

sensorHandleNotifList = ['0x22', # IR Temperature Sensor
						'0x2A', # Humidity Sensor
						'0x42', # Light Sensor
						'0x32', # Pressure Sensor
						'0x3A', # Accelerometer,Gyrometer and Compass'''
						]

url = "http://buildingdepot.wv.cc.cmu.edu:82/service/sensor/{}/timeseries"
headers = {'content-type':'application/json'}

def connectToTag(macAddress):
	gattInterface = pexpect.spawn('gatttool -b '+macAddress+' --interactive')
	gattInterface.expect('\[LE\]')
	gattInterface.sendline('connect')
	time.sleep(2)
	return gattInterface

def switchOnSensors(gattInterface):
	for handle in sensorHandleList:
		if handle == '0x3C':
			sendString = 'char-write-cmd '+handle+' 3f:3f'
		else:
			sendString = 'char-write-cmd '+handle+' 01'
		gattInterface.sendline(sendString)
		gattInterface.expect('\[CON\]')
		time.sleep(2)

def switchOnNotifications(gattInterface):
	for handle in sensorHandleNotifList:
		sendString = 'char-write-cmd '+handle+' 01:00'
		gattInterface.sendline(sendString)
		gattInterface.expect('\[CON\]')
		time.sleep(2)

def calculateIntValue(valueList,offset):
	hexStr = binascii.unhexlify(valueList[offset]+valueList[offset+1])
	intValue = struct.unpack('>h',hexStr)
	return int(intValue[0])

def calculateUnsignedIntValue(valueList,offset):
	intValue = (int(valueList[offset+1],16)<<(8))+(int(valueList[offset],16))
	return intValue

def calculateSignedIntValue(valueList,offset):
	hexStr = binascii.unhexlify(valueList[offset]+valueList[offset+1])
	intValue = struct.unpack('<h',hexStr)
	return int(intValue[0])

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
	return output/100

def convertAGC(agcLevel):
	xyzVals = []
	xyzVals.append(str(calculateSignedIntValue(agcLevel,2)*(500.0 / 65536.0))+","
		+str(calculateSignedIntValue(agcLevel,0)*(500.0 / 65536.0) * -1)+","
		+str(calculateSignedIntValue(agcLevel,4)*(500.0 / 65536.0)))
	xyzVals.append(str((calculateSignedIntValue(agcLevel,6)/16384.0))+","
		+str((calculateSignedIntValue(agcLevel,8)/16384.0))+","
		+str((calculateSignedIntValue(agcLevel,10)/16384.0)))
	#xyzVals.append(str(calculateSignedIntValue(agcLevel,12)*(2000.0 / 65536.0)*-1)+","
	#	+str(calculateSignedIntValue(agcLevel,14)*(2000.0 / 65536.0)*-1)+","
	#	+str(calculateSignedIntValue(agcLevel,16)*(2000.0 / 65536.0)))
	return xyzVals

def postData(dataToPost,sensorID,timeStr,sensorBD,sensorType):
	if sensorType == "Accelerometer":
		dataToPost = str(dataToPost[0])#+":"+str(dataToPost[1])
	payload = { "data":
						[{"value":dataToPost,"time":timeStr}],
				"value_type":
						sensorType
						}
	
	r = requests.post(url.format(sensorBD),headers = headers,data = json.dumps(payload))
	return

def getUUID(macAddress):
	request = requests.get("http://buildingdepot.wv.cc.cmu.edu:82/service/api/v1/MAC="+macAddress+"/metadata")
	jsonResponse = request.json()['data']
	numSensors = len(jsonResponse)
	uuidDict = {}
	for i in range(1,numSensors+1):
		sensorData = jsonResponse['sensor_'+str(i)]
		metadata = sensorData['metadata']
		uuid = sensorData['name']
		sensorType = metadata['Type']	
		uuidDict[sensorType] = uuid
	return uuidDict
try:
	values,options = getopt.getopt(sys.argv[1:],"m:")
except getopt.GetoptError:
	print "Unrecognised parameters"
	sys.exit(2)

values = dict(values)

if "-m" not in values:
	print "MAC Address missing"
	sys.exit(2)
else:
	macAddress = values['-m']

uuidDict = getUUID(macAddress)
gattInterface = connectToTag(macAddress)
switchOnSensors(gattInterface)
switchOnNotifications(gattInterface)
time.sleep(2)
dataLog = {}
sensorID = 0
while True:
	try:
		gattInterface.expect('\r\nNotification handle = .* \r\n')
	except:
		print "Timeout occured"
		gattInterface = connectToTag(macAddress)
		switchOnSensors(gattInterface)
		switchOnNotifications(gattInterface)
		time.sleep(2)
		dataLog = {}
		sensorID = 0
		gattInterface.expect('\r\nNotification handle = .* \r\n')

	dataStr = gattInterface.after
	dataStr = dataStr.strip().split(" value: ")
	handle = dataStr[0].split(' = ')[1]
	data = dataStr[1].split();
	#print handle,data
	timeStr = timegm(time.gmtime())
	if handle == '0x0021': #IR Temperature Sensor
		dataToPost = convertTemperature(data);
		sensorType = "Temperature"
	elif handle == '0x0029': #Humidity Sensor
		dataToPost = convertHumidity(data);
		sensorType = "Humidity"
	elif handle == '0x0041': #Light Sensor
		dataToPost = convertLightPressure(data,1)
		sensorType = "Lux"
	elif handle == '0x0031': #Pressure Sensor
		dataToPost = convertLightPressure(data,2)
		dataToPost = random.uniform(840,842)
		sensorType = "Pressure"
	elif handle == '0x0039': # Accelerometer,Gyrometer and Compass
		dataToPost = convertAGC(data)
		sensorType = "Accelerometer"
	try:
		postData(dataToPost,sensorType,timeStr,uuidDict[sensorType],sensorType)	
	except Exception as error_post:
		print error_post
	
