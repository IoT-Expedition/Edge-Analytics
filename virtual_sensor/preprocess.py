import glob
import numpy as np

class sampleSet:
    def __init__(self,features,labels):
        self.features = features
        self.labels = labels

def countZeroCrossing(data):
    count = 0
    for idx in range(len(data)-1):
        if data[idx]*data[idx+1] < 0:
            count = count + 1

    return count

def peakCount(data):
    count = 0
    std = np.std(data)
    for idx in range(len(data)-2):
        if data[idx+1] > std*2 and (data[idx+1] - data[idx]) * (data[idx+2] - data[idx+1]) < 0:
            count = count + 1

    return count

allFeatures = []

def extractFeatures(sensorReadings):
    colNum = np.shape(sensorReadings)[1]
    features = np.zeros((colNum-1,8))

    for col in range(1,colNum):
        # average
        features[col-1,0] = np.average(sensorReadings[:,col])
        
        # std
        features[col-1,1] = np.std(sensorReadings[:,col])
        
        # peak count
        features[col-1,2] = peakCount(sensorReadings[:,col])

        # median
        features[col-1,3] = np.median(sensorReadings[:,col])

        # min
        features[col-1,4] = np.min(sensorReadings[:,col])

        # max
        features[col-1,5] = np.max(sensorReadings[:,col])

        # zero crossing
        features[col-1,6] = countZeroCrossing(sensorReadings[:,col])

        # max - min
        features[col-1,7] = features[col-1,5] - features[col-1,4]

    f = features.reshape(1,(colNum-1)*8)[0]

    return f

# Main function
if __name__ == "__main__":
    for r in glob.glob('test/samples/close/*'):
        print r
        data = np.load(r)

        f = extractFeatures(data)

        if allFeatures == []:
            allFeatures = f
        else:
            allFeatures = np.vstack((allFeatures,f))

    print np.shape(allFeatures)
    np.save('test/preprocessed/close.npy',allFeatures)












