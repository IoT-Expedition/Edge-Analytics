import numpy as np

data = np.load('test.npy')
print data[1:99,0] - data[0:98,0]
