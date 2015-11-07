from __future__ import print_function

from time import time
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from sklearn.svm import SVC
from scipy.stats import randint as sp_randint
from sklearn import svm



def GridSearchParams(X, y):
    print("Fitting the classifier to the training set")
    t0 = time()
    param_grid = {'C': [1, 1e3, 5e3, 1e4, 5e4, 1e5],
                  'gamma': [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.1], }
    clf = GridSearchCV(SVC(kernel='rbf', class_weight='balanced'), param_grid, verbose=10, n_jobs=8)
    clf = clf.fit(X, y)
    print("done in %0.3fs" % (time() - t0))
    print("Best estimator found by grid search:")
    print(clf.best_estimator_)

# [Parallel(n_jobs=1)]: Done 108 out of 108 | elapsed: 32.5min finished
# done in 1956.013s
# Best estimator found by grid search:
# SVC(C=1000.0, cache_size=200, class_weight='balanced', coef0=0.0,
#   decision_function_shape=None, degree=3, gamma=0.1, kernel='rbf',
#   max_iter=-1, probability=False, random_state=None, shrinking=True,
#   tol=0.001, verbose=False)

def RandomParamSearch(X, y):
    # specify parameters and distributions to sample from
    clf = svm.SVC(kernel='rbf')
    param_dist = {"max_depth": [3, None],
                  "max_features": sp_randint(1, 11),
                  "min_samples_split": sp_randint(1, 11),
                  "min_samples_leaf": sp_randint(1, 11),
                  "bootstrap": [True, False],
                  "criterion": ["gini", "entropy"]}

    # run randomized search
    n_iter_search = 20
    clf = RandomizedSearchCV(SVC(kernel='rbf', class_weight='balanced'),
                                       param_distributions=param_dist, n_iter=n_iter_search, n_jobs=1, verbose=10)
    clf = clf.fit(X, y)
    print("done in %0.3fs" % (time() - t0))
    print("Best estimator found by grid search:")
    print(clf.best_estimator_)
    pass



