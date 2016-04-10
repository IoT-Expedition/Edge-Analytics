# sklearn functions
from sklearn.svm import LinearSVC, SVC
from sklearn.cross_validation import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.cross_validation import train_test_split
from sklearn import preprocessing
from sklearn import feature_selection
import warnings
import json
import os
from sklearn.externals import joblib
import pickle

import numpy as np

# My helpers
from preprocess import extractFeatures
from preprocess import sampleSet 

def readPredMeta(sensor):
    path = predictionDir(sensor) + 'meta.json'
    meta = json.loads(open(path,'r').read())
    return meta   

def generatePredictionData(meta,dataDir):
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

def saveObject(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def modelDir(sensor):
    return 'sensors/' + sensor + '/model/'

def dataDir(sensor):
    return 'sensors/' + sensor + '/samples/'

def predictionDir(sensor):
    return 'sensors/' + sensor + '/predictions/' 

# Read a meta file
def readMeta(sensor):
    path = dataDir(sensor) + 'meta.json'
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

def generateData(meta,labels,dataDir):
    allFeatures = []
    allLabels = []

    for sample in meta:
        # Extract features and a label
        rawData = np.genfromtxt(dataDir + sample['filename'], delimiter=',')
        features = extractFeatures(rawData)
        indexedLabel = labels.index(sample['label'])

        # Stack features and labels
        if allFeatures == []:
            allFeatures = features
        else:
            allFeatures = np.vstack((allFeatures,features))

        allLabels.append(indexedLabel)

    data = sampleSet(allFeatures,allLabels)

    return data

# Train a classifer for a given sensor and save it
def trainClassifier(sensor):
    # Load meta informaton about samplings
    meta = readMeta(sensor)

    # Geenrate a trainig set
    labels = generateLabels(meta)
    data = generateData(meta, labels, dataDir(sensor))

    # Prescaling
    scaler = preprocessing.Scaler().fit(data.features)
    scaledFeatures = scaler.transform(data.features)

    # Feature selection
    selector = feature_selection.SelectKBest(feature_selection.f_regression).fit(scaledFeatures, data.labels)
    selectedFeatures = selector.transform(scaledFeatures)

    # Train a classifier
    clf = SVC(kernel='linear', C=1).fit(selectedFeatures, data.labels)

    # Save to files
    if not os.path.exists(modelDir(sensor)):
        os.makedirs(modelDir(sensor))
    joblib.dump(clf, modelDir(sensor) + 'model.pkl')
    joblib.dump(scaler, modelDir(sensor) + 'scaler.pkl')
    joblib.dump(selector, modelDir(sensor) + 'selector.pkl')
    saveObject(labels, modelDir(sensor)+'labels.pkl')

def crossValidation(sensor):
    meta = readMeta(sensor)

    # Geenrate a trainig set
    labels = generateLabels(meta)
    data = generateData(meta, labels, dataDir(sensor))

    # Prescaling
    scaler = preprocessing.Scaler().fit(data.features)
    scaledFeatures = scaler.transform(data.features)

    # Feature selection
    selector = feature_selection.SelectKBest(feature_selection.f_regression).fit(scaledFeatures, data.labels)
    selectedFeatures = selector.transform(scaledFeatures)

    # Train a classifier
    clf = SVC(kernel='linear', C=1)

    scores = cross_val_score(clf, selectedFeatures, data.labels, cv=5)
    return scores


# Main function
if __name__ == "__main__":
    warnings.filterwarnings('ignore')
    sensor = 'knocking'

    trainClassifier(sensor)
    crossValidation(sensor)
    print "Finished training"

