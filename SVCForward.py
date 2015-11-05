import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm, preprocessing
import pandas as pd
from matplotlib import style
style.use('ggplot')
import matplotlib.dates
from datetime import datetime
how_much_better = 5

def status_calc(stock_p_change, sp500_p_change):

    difference = stock_p_change-sp500_p_change
    if difference > 10:
        return 1
    else:
        return 0


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
    data_df = pd.DataFrame.from_csv(file, parse_dates=['Date'])

    data_df = data_df.reindex(np.random.permutation(data_df.index))
    data_df = data_df.replace('N/A',0).replace('NaN',0)
    data_df['Status'] = map(status_calc, data_df['stock_p_change'], data_df['sp500_p_change'])


    X = np.array(data_df[features].values)
    X = preprocessing.scale(X)

    alpha = np.array(data_df[['stock_p_change', 'sp500_p_change']])
    return X, y, alpha, data_df


def Analysis():

    test_size = 1000
    file = path + 'key_stats_acc_perf_WITH_NA.csv'
    invest_amount = 100.
    total_invests = 0.
    if_market = 0.
    if_strat = 0.

    X, y, alpha, Z = Build_Data_Set(file, FEATURES)

    clf = svm.SVC(kernel='rbf', tol=1e-5, C=1.0)
    #clf = svm.SVC(kernel='linear', C=1.0)

    clf.fit(X[:-test_size], y[:-test_size])  # training size

    correct_count = 0
    for x in range(test_size + 1):
        if clf.predict(X[-x])[0] == y.values[-x]:
            correct_count += 1

    for x in range(test_size + 1):
        if clf.predict(X[-x])[0] == 1:
            invest_return = invest_amount + invest_amount * alpha[-x][0] / 100.
            market_return = invest_amount + invest_amount * alpha[-x][1] / 100.
            total_invests += 1
            if_market += market_return
            if_strat += invest_return

    print 'Accuracy : %' + str(float(correct_count)/test_size * 100.0)
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


    data_df = pd.DataFrame.from_csv(path+'forward_sample_WITH_NA.csv')
    data_df = data_df.replace('N/A',0).replace('NaN',0)

    invest_list = []

    X = np.array(data_df[FEATURES].values)
    X = preprocessing.scale(X)
    tickers = data_df['ticker'].values.tolist()

    for i in range(len(X)):
        p = clf.predict(X[i])[0]
        if p == 1:
            print tickers[i]
            invest_list.append(tickers[i])

    print len(invest_list)
    print invest_list

    ts_dict = {name: pd.Series(group['stock_price'].values, index=group['Date'].values) for (name, group) in Z.groupby('ticker')}

    for e in invest_list:
        if e in ts_dict.keys():
            ts_dict[e].plot()
            plt.xlabel('date')
            plt.ylabel('stock price')
    plt.show()

Analysis()