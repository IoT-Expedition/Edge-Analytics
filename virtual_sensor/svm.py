# sklearn functions
from sklearn.svm import LinearSVC, SVC
from sklearn.cross_validation import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.cross_validation import train_test_split
from sklearn import preprocessing
import warnings

# numpy
import numpy as np

warnings.filterwarnings('ignore')

dataOpen = np.load('test/preprocessed/open.npy')
dataClose = np.load('test/preprocessed/close.npy')

labelOpen = np.ones(len(dataOpen))
labelClose = np.zeros(len(dataClose))

features = np.vstack((dataOpen,dataClose))
labels = np.append(labelOpen,labelClose)

#test_features = data.features        # features
#test_labels   = data.labels          # labels

X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.4, random_state=0)

clf = SVC(kernel='linear', C=1).fit(X_train, y_train)
print clf.score(X_test, y_test) 

#test_features = scaler.transform(test_features)

#clf = SVC(C=1.0,max_iter=100000)
#clf.fit(features,labels)

#print(clf.score(test_features,test_labels))
