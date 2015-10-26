import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm, preprocessing
import pandas as pd
from matplotlib import style
style.use('ggplot')


path = '/Users/marcel/workspace/data/'
FEATURES =  ['DE Ratio',
             'Trailing P/E',
             'Price/Sales',
             'Price/Book',
             'Profit Margin',
             'Operating Margin',
             'Return on Assets',
             'Return on Equity',
             'Revenue Per Share',
             'Market Cap',
             'Forward P/E',
             'PEG Ratio',
             'Enterprise Value',
             'Revenue',
             'Gross Profit',
             'EBITDA',
             'Net Income Avl to Common ',
             'Earnings Per Share',
             'Earnings Growth',
             'Revenue Growth',
             'Total Cash',
             'Total Cash Per Share',
             'Total Debt',
             'Current Ratio',
             'Book Value Per Share',
             'Operating Cash Flow',
             'Beta',
             'Held by Insiders',
             'Held by Institutions',
             'Shares Short',
             'Short Ratio',
             'Short % of Float']

def Build_Data_Set(features):
    data_df = pd.DataFrame.from_csv(path+'output/key_stats_without_NA.csv')

    data_df = data_df.reindex(np.random.permutation(data_df.index))
    X = data_df[features]

    y = data_df['Status']\
        .replace('underperform', 0)\
        .replace('outperform', 1)
    X = preprocessing.scale(X)
    return X, y

def Analysis2D():
    X,y = Build_Data_Set(['DE Ratio', 'Trailing P/E'])

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

def Analysis():

    test_size = 2500

    X,y = Build_Data_Set(FEATURES)
    print len(X)

    clf = svm.SVC(kernel='rbf', tol=1e-5, C=1.0)
    #clf = svm.SVC(kernel='linear', C=1.0)

    clf.fit(X[:-test_size], y[:-test_size])  # training size

    correct_count = 0
    for x in range(test_size + 1):
        if clf.predict(X[-x])[0] == y.values[-x]:
            correct_count += 1.

    print 'Accuracy : ' + str(correct_count/test_size * 100.0) +'%'

    pass

Analysis()