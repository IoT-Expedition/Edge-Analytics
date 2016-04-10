import numpy as np

data = np.load('./test/rawdata/doorOpen.npy')
np.savetxt('doorOpen1.csv', data, delimiter=',')
