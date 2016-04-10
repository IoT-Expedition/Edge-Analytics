import numpy as np

filename = 'doorClose3'

data = np.load('./test/rawdata/'+filename + '.npy')

for i in range(10):
    sample = data[i*9:i*9+8,:]
    np.save('./test/samples/close/'+filename + '-' + str(i) + '.npy',sample)
