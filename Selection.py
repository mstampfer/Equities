import numpy as np
from sklearn import svm

class Selection(object):
    def __init__(self, X, y, features, cv_size):
        self.X = X
        self.y = y
        self.features = features
        self.cv_size = cv_size

    def selectC(self, X ,y):

        bestF1 = 0
        bestC = 0
        cGen = (c for c in [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 ])

        for C in cGen:
            clf = svm.SVC(kernel='rbf', tol=1e-5, C=C)
            #clf = svm.SVC(kernel='linear', C=C)

            clf.fit(X[:-self.cv_size], y[:-self.cv_size])  # training size

            predictions = clf.predict(X[-self.cv_size:])
            y_cv = y[-self.cv_size:]
            tp = np.sum(y_cv & predictions)
            fp = np.sum(predictions & np.logical_xor(predictions, y_cv))
            fn = np.sum(y_cv & np.logical_xor(predictions, y_cv))
            tn = np.sum(np.logical_not(y_cv, predictions))

            if (tp + fp) and (tp + fn) and tp:
                precision = float(tp)/(tp + fp)
                recall = float(tp)/(tp + fn)
                F1 = 2.0 * precision * recall/(precision + recall)
            else:
                F1 = 0
            try:
                mcc = float(tp*tn - fp*fn)/np.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))
            except:
                mcc = tp*tn - fp*fn

            if F1 > bestF1:
                bestF1 = F1
                bestC = C
            print "\nbest C: %f\nbest F1 %f\nthis mcc %f\n" %(bestC, bestF1, mcc)

        return bestC