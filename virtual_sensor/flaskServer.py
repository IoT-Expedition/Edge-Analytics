from flask import Flask
import os
import json
from train import trainClassifier, crossValidation, readMeta
from predict import makePrediction
from flask import request
import numpy as np
import glob
from sensorHandler import sensorHandler

VIRTUAL_SENSOR_DIR = '/home/pi/virtual_sensor/'

app = Flask(__name__)

def jsonString(obj,pretty=True):
    if pretty == True:
        return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')) + '\n'
    else:
        return json.dumps(obj)

@app.route("/")
def hello():
	return "Raspberry Pi for GIoTTO"

@app.route('/sensor/<sensorName>', methods=['GET','POST','DELETE'])
def showSensorProfile(sensorName):
    if request.method == 'POST':
        baseDir = 'sensors/'
        sensorHdl = sensorHandler(baseDir);
        sensorHdl.addSensor(sensorName)
        return  '{"result":"OK","message":"sensor created"}'
    elif request.method == 'GET':
        baseDir = 'sensors/'
        sensorHdl = sensorHandler(baseDir);
        result = sensorHdl.evaluateSensor(sensorName)

        #scores = crossValidation(sensorName)
        #meta = readMeta(sensorName)
        #result = {'result':'OK','sampleNum':len(meta),'accuracies':scores.tolist(), 'meanAccuracy':np.average(scores).tolist()}
        return jsonString(result)
    elif request.method == 'DELETE':
        baseDir = 'sensors/'
        sensorHdl = sensorHandler(baseDir);
        sensorHdl.deleteSensor(sensorName)
        return  '{"result":"OK","message":"sensor deleted"}'

@app.route('/sensor/<sensorName>/samples', methods=['GET','DELETE'])
def manageSampledData(sensorName):
    if request.method == 'GET':
        return "GET"
    elif request.method == 'DELETE':
        for path in glob.glob(VIRTUAL_SENSOR_DIR + 'samples/*'):
            os.remove(path)
        result = {"result":"OK"}
        return jsonString(result)


@app.route('/sensor/<sensor>/sample/<label>')
def sampleDataWithLabel(sensor,label):
    # create a lock file to avoid collision
    lockPath = VIRTUAL_SENSOR_DIR + 'cmd/lock'
    command = {'command' : 'sample' , 'sensor' : sensor , 'label' : label , 'sampleNum' : 3}

    open(lockPath, 'a').close()

    with open(VIRTUAL_SENSOR_DIR + 'cmd/cmd', 'w') as f:
        f.write(jsonString(command))

    os.remove(lockPath)

    result = {"result":"OK"}
    return jsonString(result)

@app.route('/sensor/<sensor>/model/train')
def train(sensor):
    trainClassifier(sensor)
    result = {"result":"OK"}
    return jsonString(result)

@app.route('/sensor/<sensor>/model/predict')
def predict(sensor):
    pred = makePrediction(sensor)
    result = {"result":"OK", "prediction":pred}
    return jsonString(result)

if __name__=="__main__":
	app.run(host='0.0.0.0', debug=True)
