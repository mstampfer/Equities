import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm, preprocessing
import pandas as pd
from matplotlib import style
style.use('ggplot')


path = '/Users/marcel/workspace/data/'

def Build_Data_Set(features={'DE Ratio', 'Trailing P/E'}):
    data_df = pd.DataFrame.from_csv(path+'output/key_stats_without_NA.csv')
    X = data_df[list(features)]
    X['DE Ratio'] = X['DE Ratio'].str.replace(",","").astype(float)
    X['Trailing P/E'] = X['Trailing P/E'].str.replace(",","").astype(float)
    y = data_df['Status']\
        .replace('underperform', 0)\
        .replace('outperform', 1)
    X = preprocessing.scale(X)
    return X, y

def Analysis():
    X,y = Build_Data_Set()

    clf = svm.SVC(kernel='linear', C=1.0)
    clf.fit(X, y)

    w = clf.coef_[0]
    a = -w[0] / w[1]
    xx = np.linspace(min(X[:, 0]), max(X[:, 0]))
    yy = a - xx*clf.intercept_[0] / w[1]

    hp = plt.plot(xx, yy, 'k-', label='non weighted')
    plt.scatter(X[:, 0], X[:, 1])

    plt.show()
    plt.xlabel('DE Ratio')
    plt.ylabel('Trailing P/E')
    pass


Analysis()