import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm, preprocessing
import pandas as pd
from matplotlib import style
style.use('ggplot')


path = '/Users/marcel/workspace/Equities/data/'
FEATURES =  [#'stock_price',
              'DE Ratio',
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

def Build_Data_Set(file, features):
    data_df = pd.DataFrame.from_csv(file)

    data_df = data_df.reindex(np.random.permutation(data_df.index))
    data_df = data_df.replace('N/A',0).replace('NaN',0).replace(',','')

    X = data_df[features]
    y = data_df['Status']\
        .replace('underperform', 0)\
        .replace('outperform', 1)
    X = preprocessing.scale(X)

    Z = np.array(data_df[['stock_p_change', 'sp500_p_change']])

    return X, y, Z

def Analysis2D():

    file = path+'key_stats.csv'
    X,y, _ = Build_Data_Set(file, ['DE Ratio', 'Trailing P/E'])

    clf = svm.SVC(kernel='linear', C=1.0)
    clf.fit(X, y)

    w = clf.coef_[0]
    a = -w[0] / w[1]
    xx = np.linspace(min(X[:, 0]), max(X[:, 0]))
    yy = a - xx*clf.intercept_[0] / w[1]

    plt.plot(xx, yy, 'k-', label='non weighted')
    plt.scatter(X[:, 0], X[:, 1])

    plt.show()
    plt.xlabel('DE Ratio')
    plt.ylabel('Trailing P/E')


def Analysis():

    test_size = 1000
    file = path+'key_stats.csv'
#    file = path+'key_stats_acc_perf_NO_NA.csv'
    invest_amount = 100.
    total_invests = 0.
    if_market = 0.
    if_strat = 0.


    X, y, Z = Build_Data_Set(file, FEATURES)
    print len(X)

    clf = svm.SVC(kernel='rbf', tol=1e-5, C=1.0)
    #clf = svm.SVC(kernel='linear', C=1.0)

    clf.fit(X[:-test_size], y[:-test_size])  # training size

    correct_count = 0
    for x in range(test_size + 1):
        if clf.predict(X[-x])[0] == y.values[-x]:
            correct_count += 1

    for x in range(test_size + 1):
        if clf.predict(X[-x])[0] == 1:
            invest_return = invest_amount + (invest_amount * Z[-x][0]/100.)
            market_return = invest_amount + (invest_amount * Z[-x][1]/100.)
            total_invests += 1
            if_market += market_return
            if_strat += invest_return

    print 'Accuracy : %s%%' % str(float(correct_count)/float(test_size) * 100.0)
    print 'Total Trades: %d' % total_invests
    print 'Ending with Strategy %f' % if_strat
    print 'Ending with Market %f' % if_market

    compared = (if_strat - if_market)/if_market * 100.
    do_nothing = total_invests * invest_amount

    avg_strat = (if_strat - do_nothing)/do_nothing * 100.
    avg_market = (if_market - do_nothing)/do_nothing * 100.


    print 'Compared to the market we earn %f more' %compared
    print 'Average investment return %f %%' %avg_strat
    print 'Average market return %f %%' %avg_market

    plt.scatter(Z[:, 0], Z[:, 1])
    plt.xlabel('stock_p_change')
    plt.ylabel('sp500_p_change')
    plt.show()
Analysis()