import struct
import math
import sys,getopt
import time
import struct
import binascii
import numpy as np
import time
import glob
import os
import json
import threading
import shutil
from train import trainClassifier, crossValidation, readMeta


class sensorHandler:
    def __init__(self, baseDir):
        self.baseDir = 'sensors/'
        self.dataDirs = dirs = {'samples/','predictions/','cmd/'}
        print "init"

    # create directories for a sensor
    def addSensor(self, sensorId):
        sensorDir = self.baseDir + sensorId + '/'
        
        for directory in self.dataDirs:
            if not os.path.exists(sensorDir + directory):
                os.makedirs(sensorDir + directory)

        if not os.path.exists(sensorDir + 'meta.json'):
            meta = json.dumps([])
            open(sensorDir + 'meta.json', 'w').write(meta)

    def deleteSensor(self, sensorId):
        shutil.rmtree(self.baseDir + sensorId + '/');

    def evaluateSensor(self,sensorId):
        scores = crossValidation(sensorId)
        meta = readMeta(sensorId)
        result = {'result':'OK','sampleNum':len(meta),'accuracies':scores.tolist(), 'meanAccuracy':np.average(scores).tolist()}
        return result
    
if __name__ == "__main__":
    print "Sensor Handler"
    sensorHandler = sensorHandler('sensors/')
    sensorHandler.addSensor('1')
        
