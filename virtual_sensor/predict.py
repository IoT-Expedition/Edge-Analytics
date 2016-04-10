# sklearn functions
from sklearn.svm import LinearSVC, SVC
from sklearn.cross_validation import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.cross_validation import train_test_split
from sklearn import preprocessing
import warnings
import json
import os
from sklearn.externals import joblib

import numpy as np
import pickle
import time

# My helpers
from preprocess import extractFeatures
from preprocess import sampleSet 

def loadObject(filename):
    with open(filename, 'r') as input:
        obj = pickle.load(input)

    return obj

def modelDir(sensor):
    return 'sensors/' + sensor + '/model/'

def dataDir(sensor):
    return 'sensors/' + sensor + '/samples/'

def predictionDir(sensor):
    return 'sensors/' + sensor + '/predictions/'    

def commandDir(sensor):
    return 'cmd/'

# Read a meta file
def readMeta(sensor):
    path = predictionDir(sensor) + 'meta.json'
    meta = json.loads(open(path,'r').read())
    return meta   

# Generate a list of labels from meta.json
def generateLabels(meta):
    labels = []
    for sample in meta:
        labels.append(sample['label'])

    # Remove duplicate
    output = []
    for i in labels:
        if not i in output:
            output.append(i)

    return output

def generateData(meta,dataDir):
    allFeatures = []
    allLabels = []

    for sample in meta:
        # Extract features and a label
        rawData = np.genfromtxt(dataDir + sample['filename'], delimiter=',')
        features = extractFeatures(rawData)

        # Stack features and labels
        if allFeatures == []:
            allFeatures = features
        else:
            allFeatures = np.vstack((allFeatures,features))

    return allFeatures

def makePrediction(sensor):
    # create a lock file to avoid collision
    lockPath = commandDir(sensor) + 'lock'
    open(lockPath, 'a').close()

    command = {"command":"predict", "sensor":sensor, "sampleNum":3}

    with open(commandDir(sensor) + 'cmd', 'w') as f:
        f.write(json.dumps(command))

    os.remove(lockPath)

    while not os.path.exists(predictionDir(sensor)+'meta.json'):
        time.sleep(0.1)
    time.sleep(1)

    # Read labels from meta.json
    meta = readMeta(sensor)

    features = generateData(meta, predictionDir(sensor))

    # prescaling
    scaler = joblib.load(modelDir(sensor)+'scaler.pkl') 
    scaledFeatures = scaler.transform(features)

    # Feture selection
    selector = joblib.load(modelDir(sensor)+'selector.pkl') 
    selectedFeatures = selector.transform(scaledFeatures)

    clf = joblib.load(modelDir(sensor)+'model.pkl')
    predictions = clf.predict(selectedFeatures)

    labels = loadObject(modelDir(sensor)+'labels.pkl')

    for p in predictions:
        print labels[p.astype(int)]

    for sample in meta:
        os.remove(predictionDir(sensor) + sample['filename'])
    os.remove(predictionDir(sensor) + 'meta.json')


    #pred = hardCoded(data)
    #return pred

    return labels[predictions[predictions.size-1].astype(int)]

def predictWithData(sensor,data):

    pred = hardCoded(data)
    return pred

    # Read labels from meta.json
    #meta = readMeta(sensor)

    features = extractFeatures(data)

    # prescaling
    scaler = joblib.load(modelDir(sensor)+'scaler.pkl') 
    scaledFeatures = scaler.transform(features)

    # Feture selection
    selector = joblib.load(modelDir(sensor)+'selector.pkl') 
    selectedFeatures = selector.transform(scaledFeatures)

    clf = joblib.load(modelDir(sensor)+'model.pkl')
    predictions = clf.predict(selectedFeatures)

    labels = loadObject(modelDir(sensor)+'labels.pkl')

    return labels[predictions[0].astype(int)]

def hardCoded(data):
    acc = data[:,6]
    d = np.max(acc) - np.min(acc)
    if(d > 2):
        return 'knocking'
    else:
        return 'silent'
    

# Main function
if __name__ == "__main__":
    warnings.filterwarnings('ignore')
    sensor = 'knocking2'


     # Read labels from meta.json

    rawData = np.genfromtxt('./sensors/knocking2/samples/1.csv', delimiter=',')
    prediction = predictWithData(sensor,rawData);
    print prediction


    #for sample in meta:
        #os.remove(predictionDir(sensor) + sample['filename'])
    #os.remove(predictionDir(sensor) + 'meta.json')


