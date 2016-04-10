import glob
import numpy as np

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

for r in glob.glob('test/samples/close/*'):
    print r
    data = np.load(r)

    colNum = np.shape(data)[1]
    features = np.zeros((colNum-1,8))

    for col in range(1,colNum):
        print col
        # average
        features[col-1,0] = np.average(data[:,col])
        
        # std
        features[col-1,1] = np.std(data[:,col])
        
        # peak count
        features[col-1,2] = peakCount(data[:,col])

        # median
        features[col-1,3] = np.median(data[:,col])

        # min
        features[col-1,4] = np.min(data[:,col])

        # max
        features[col-1,5] = np.max(data[:,col])

        # zero crossing
        features[col-1,6] = countZeroCrossing(data[:,col])

        # max - min
        features[col-1,7] = features[col-1,5] - features[col-1,4]

    f = features.reshape(1,(colNum-1)*8)[0]
    if allFeatures == []:
        allFeatures = f
    else:
        allFeatures = np.vstack((allFeatures,f))

print np.shape(allFeatures)
np.save('test/preprocessed/close.npy',allFeatures)












